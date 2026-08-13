import hashlib
import json
import logging
from datetime import timedelta

from django.conf import settings
from django.core import signing
from django.utils import timezone
from django.db import models, transaction
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.selectors import villages_for_user
from apps.core.security.confidentiality import permitted_section_codes, role_codes_for_user
from apps.reporting.models import ReportingPeriod, ReportSectionStatus
from apps.reporting.section_registry import SECTION_ENTRIES
from apps.reporting.selectors import reports_for_user
from apps.reporting.progress import recalculate_report_progress
from apps.workflow.services import available_actions
from apps.workflow.models import FinalDeclaration
from apps.workflow.services import transition_report
from apps.data_quality.services import validate_report
from apps.accounts.permissions import REPORT_AUTHOR_ROLE_CODES, user_has_any_role
from apps.audit.services import record_event
from apps.documents.models import EvidenceDocument, EvidenceLink
from apps.core.security import can_view_analytics, can_view_document
from apps.analytics.models import IndicatorValue
from apps.reporting.amendments import apply_indicator_overrides

from .models import ApiIdempotencyRecord, MobileDevice, MobileSyncSession
from .sync import MAX_BATCH_RECORDS, apply_change, authoritative_changes
from .serializers import (
    DeviceLoginSerializer,
    DeviceLoginResponseSerializer,
    DeviceRefreshSerializer,
    LocationAssignmentSerializer,
    ReportingPeriodSerializer,
    ReportCreateSerializer,
    ReportSerializer,
    VillageSerializer,
)
from .versioning import app_version_policy


logger = logging.getLogger("tnk.mobile_api")


def user_payload(user):
    assignments = user.location_assignments.filter(is_active=True).select_related("province", "tikina", "village")
    return {
        "uuid": user.uuid,
        "username": user.username,
        "full_name": user.get_full_name(),
        "preferred_language": user.preferred_language,
        "roles": sorted(role_codes_for_user(user)),
        "location_assignments": LocationAssignmentSerializer(assignments, many=True).data,
        "record_version": user.record_version,
    }


def mobile_field_definition(model, field_name):
    field = model._meta.get_field(field_name)
    if field.choices:
        field_type = "choice"
    elif field.is_relation:
        field_type = "relation"
    elif isinstance(field, models.BooleanField):
        field_type = "boolean"
    elif isinstance(field, models.DateTimeField):
        field_type = "datetime"
    elif isinstance(field, models.DateField):
        field_type = "date"
    elif isinstance(field, models.IntegerField):
        field_type = "integer"
    elif isinstance(field, (models.DecimalField, models.FloatField)):
        field_type = "decimal"
    else:
        field_type = "text"
    return {
        "name": field_name,
        "label": str(field.verbose_name).capitalize(),
        "type": field_type,
        "required": not field.blank and not field.null,
        "max_length": getattr(field, "max_length", None),
        "choices": [{"value": str(value), "label": str(label)} for value, label in field.flatchoices],
    }


class DeviceLoginView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "mobile_login"

    @extend_schema(
        request=DeviceLoginSerializer,
        responses={
            200: DeviceLoginResponseSerializer,
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Validation error. The response contains a code and field-specific message lists.",
            ),
        },
    )
    def post(self, request):
        serializer = DeviceLoginSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            if settings.DEBUG:
                logger.warning(
                    "Mobile login validation failed: request_fields=%s validation_fields=%s validation_messages=%s",
                    sorted(request.data.keys()) if isinstance(request.data, dict) else [],
                    sorted(serializer.errors.keys()),
                    {
                        field: [str(message) for message in messages]
                        for field, messages in serializer.errors.items()
                    },
                    extra={
                        "event": "mobile_login_validation_failed",
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "method": request.method,
                        "path": request.path,
                    },
                )
            raise serializers.ValidationError(serializer.errors)
        return Response(serializer.validated_data)


class DeviceTokenRefreshView(TokenRefreshView):
    permission_classes = (AllowAny,)
    authentication_classes = ()
    serializer_class = DeviceRefreshSerializer


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=inline_serializer("LogoutRequest", fields={"refresh": serializers.CharField()}),
        responses={204: None},
    )
    def post(self, request):
        refresh_value = request.data.get("refresh")
        if not refresh_value:
            return Response({"code": "validation_error", "detail": "A refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            refresh = RefreshToken(refresh_value)
            if str(refresh.get("device_uuid", "")) != str(request.auth.get("device_uuid", "")):
                return Response({"code": "permission_denied", "detail": "Token device mismatch."}, status=status.HTTP_403_FORBIDDEN)
            refresh.blacklist()
        except TokenError:
            return Response({"code": "invalid_token", "detail": "The refresh token is invalid."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        return Response(user_payload(request.user))

    @extend_schema(request=inline_serializer("LanguagePreference", fields={"preferred_language": serializers.ChoiceField(choices=("en", "fj"))}), responses={200: OpenApiTypes.OBJECT})
    def patch(self, request):
        serializer = serializers.Serializer(data=request.data)
        serializer.fields["preferred_language"] = serializers.ChoiceField(choices=("en", "fj"))
        serializer.is_valid(raise_exception=True)
        request.user.preferred_language = serializer.validated_data["preferred_language"]
        request.user.save(update_fields=("preferred_language", "record_version"))
        return Response(user_payload(request.user))


class VillageListView(generics.ListAPIView):
    serializer_class = VillageSerializer

    def get_queryset(self):
        return villages_for_user(self.request.user).select_related("tikina__province")


class ReportingPeriodListView(generics.ListAPIView):
    serializer_class = ReportingPeriodSerializer

    def get_queryset(self):
        return ReportingPeriod.objects.filter(is_open=True, is_locked=False)


class ReportListCreateView(generics.ListCreateAPIView):
    def get_queryset(self):
        return reports_for_user(self.request.user).select_related("village", "reporting_period", "previous_report").prefetch_related("section_statuses")

    def get_serializer_class(self):
        return ReportCreateSerializer if self.request.method == "POST" else ReportSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = serializer.save()
        return Response(ReportSerializer(report).data, status=status.HTTP_201_CREATED)


class ReportDetailView(generics.RetrieveAPIView):
    serializer_class = ReportSerializer
    lookup_field = "uuid"

    def get_queryset(self):
        return reports_for_user(self.request.user).select_related("village", "reporting_period", "previous_report").prefetch_related("section_statuses")


class BootstrapView(APIView):
    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        user = request.user
        device = MobileDevice.objects.get(uuid=request.auth["device_uuid"], user=user)
        reports = reports_for_user(user).select_related("village", "reporting_period", "previous_report").prefetch_related("section_statuses")
        villages = villages_for_user(user).select_related("tikina__province")
        section_codes = permitted_section_codes(user)
        section_definitions = [
            {
                "code": code,
                "label": label,
                "entry_types": [
                    {
                        "key": entry.key,
                        "label": entry.label,
                        "fields": entry.fields,
                        "field_definitions": [mobile_field_definition(entry.model, field) for field in entry.fields],
                        "allow_create": entry.allow_create,
                        "allow_delete": entry.allow_delete,
                    }
                    for entry in SECTION_ENTRIES.get(code, ())
                ],
            }
            for code, label in ReportSectionStatus.Section.choices
            if code in section_codes
        ]
        bootstrap_time = timezone.now()
        device.last_sync_at = bootstrap_time
        device.save(update_fields=("last_sync_at", "last_seen_at"))
        return Response({
            "schema_version": 1,
            "server_time": bootstrap_time,
            "sync_cursor": None,
            "user": user_payload(user),
            "device": {
                "uuid": device.uuid,
                "platform": device.platform,
                "app_version": device.app_version,
                "version_policy": app_version_policy(device.app_version),
            },
            "villages": VillageSerializer(villages, many=True).data,
            "reporting_periods": ReportingPeriodSerializer(ReportingPeriod.objects.filter(is_open=True, is_locked=False), many=True).data,
            "reports": ReportSerializer(reports, many=True).data,
            "section_definitions": section_definitions,
            "workflow_capabilities": {str(report.uuid): available_actions(report, user) for report in reports},
        })


class SyncChangesView(APIView):
    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        try:
            payload = authoritative_changes(request.user, request.query_params.get("cursor"))
        except signing.BadSignature:
            return Response(
                {"code": "invalid_cursor", "detail": "The sync cursor is invalid or expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        device = MobileDevice.objects.get(uuid=request.auth["device_uuid"], user=request.user)
        device.last_sync_at = payload["server_time"]
        device.save(update_fields=("last_sync_at", "last_seen_at"))
        return Response(payload)


class SyncBatchView(APIView):
    @extend_schema(request=OpenApiTypes.OBJECT, responses={200: OpenApiTypes.OBJECT})
    def post(self, request):
        changes = request.data.get("changes")
        if not isinstance(changes, list):
            return Response({"code": "validation_error", "detail": "changes must be a list."}, status=400)
        if len(changes) > MAX_BATCH_RECORDS:
            return Response({"code": "batch_too_large", "detail": f"A batch may contain at most {MAX_BATCH_RECORDS} records."}, status=413)
        device = MobileDevice.objects.get(uuid=request.auth["device_uuid"], user=request.user)
        sync_session = MobileSyncSession.objects.create(user=request.user, device=device)
        results = [apply_change(user=request.user, device=device, item=item) for item in changes]
        accepted = [item for item in results if item["status"] == "accepted"]
        conflicts = [item for item in results if item["status"] == "conflict"]
        failed = [item for item in results if item["status"] == "failed"]
        sync_session.uploaded_count = len(accepted)
        sync_session.conflict_count = len(conflicts)
        sync_session.failed_count = len(failed)
        sync_session.completed_at = timezone.now()
        sync_session.status = MobileSyncSession.Status.COMPLETED if not conflicts and not failed else MobileSyncSession.Status.PARTIAL
        sync_session.save(update_fields=("uploaded_count", "conflict_count", "failed_count", "completed_at", "status"))
        device.last_sync_at = sync_session.completed_at
        device.save(update_fields=("last_sync_at", "last_seen_at"))
        return Response({"sync_session_uuid": sync_session.uuid, "accepted": accepted, "conflicts": conflicts, "failed": failed})


def evidence_payload(document):
    return {
        "uuid": str(document.uuid),
        "title": document.title,
        "document_type": document.document_type,
        "original_filename": document.original_filename,
        "file_size": document.file_size,
        "mime_type": document.mime_type,
        "checksum": document.checksum,
        "description": document.description,
        "confidentiality_level": document.confidentiality_level,
        "captured_at": document.captured_at.isoformat() if document.captured_at else None,
        "latitude": str(document.latitude) if document.latitude is not None else None,
        "longitude": str(document.longitude) if document.longitude is not None else None,
        "location_accuracy_metres": str(document.location_accuracy_metres) if document.location_accuracy_metres is not None else None,
        "uploaded_at": document.uploaded_at.isoformat(),
    }


class ReportEvidenceView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def _report(self, request, report_uuid):
        return generics.get_object_or_404(reports_for_user(request.user), uuid=report_uuid)

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request, report_uuid):
        report = self._report(request, report_uuid)
        content_type = ContentType.objects.get_for_model(report)
        documents = EvidenceDocument.objects.filter(links__content_type=content_type, links__object_id=report.pk)
        return Response([evidence_payload(document) for document in documents if can_view_document(request.user, document)])

    @extend_schema(request=OpenApiTypes.OBJECT, responses={201: OpenApiTypes.OBJECT})
    @transaction.atomic
    def post(self, request, report_uuid):
        report = self._report(request, report_uuid)
        if not report.is_editable or not user_has_any_role(request.user, REPORT_AUTHOR_ROLE_CODES):
            return Response({"code": "permission_denied", "detail": "This report cannot accept evidence."}, status=403)
        key_value = request.headers.get("Idempotency-Key")
        try:
            key = __import__("uuid").UUID(key_value or "")
        except ValueError:
            return Response({"code": "validation_error", "detail": "A valid Idempotency-Key header is required."}, status=400)
        device = MobileDevice.objects.get(uuid=request.auth["device_uuid"], user=request.user)
        upload = request.FILES.get("file")
        if upload is None:
            return Response({"code": "validation_error", "detail": "An evidence file is required."}, status=400)
        digest = hashlib.sha256()
        for chunk in upload.chunks():
            digest.update(chunk)
        upload.seek(0)
        request_checksum = digest.hexdigest()
        metadata_digest = hashlib.sha256()
        metadata_digest.update(request_checksum.encode())
        metadata_digest.update(
            json.dumps(
                {key: request.data.get(key, "") for key in (
                    "title", "document_type", "description", "confidentiality_level",
                    "captured_at", "latitude", "longitude", "location_accuracy_metres",
                )},
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        )
        request_fingerprint = metadata_digest.hexdigest()
        replay = ApiIdempotencyRecord.objects.filter(user=request.user, device=device, key=key).first()
        if replay:
            if replay.endpoint != "reports/evidence" or replay.request_hash != request_fingerprint:
                return Response({"code": "idempotency_mismatch", "detail": "That idempotency key was used for another request."}, status=409)
            return Response(replay.response_body, status=replay.response_status)
        document = EvidenceDocument(
            uuid=key,
            title=request.data.get("title", ""),
            document_type=request.data.get("document_type", ""),
            file=upload,
            original_filename=upload.name,
            file_size=upload.size,
            mime_type=getattr(upload, "content_type", "application/octet-stream"),
            checksum="pending",
            description=request.data.get("description", ""),
            confidentiality_level=request.data.get("confidentiality_level", "restricted"),
            captured_at=request.data.get("captured_at") or None,
            latitude=request.data.get("latitude") or None,
            longitude=request.data.get("longitude") or None,
            location_accuracy_metres=request.data.get("location_accuracy_metres") or None,
            uploaded_by=request.user,
        )
        try:
            document.full_clean(exclude=("checksum",))
            document.save()
        except ValidationError as error:
            return Response({"code": "validation_error", "errors": error.message_dict}, status=400)
        EvidenceLink.objects.create(document=document, content_type=ContentType.objects.get_for_model(report), object_id=report.pk)
        payload = evidence_payload(document)
        ApiIdempotencyRecord.objects.create(
            user=request.user, device=device, key=key, endpoint="reports/evidence",
            request_hash=request_fingerprint, response_status=201, response_body=payload,
            expires_at=timezone.now() + timedelta(days=30),
        )
        record_event(actor=request.user, action="document.uploaded", instance=document, summary=f"Uploaded mobile evidence for {report}")
        return Response(payload, status=201)


def quality_issue_payload(issue):
    return {
        "uuid": str(issue.uuid),
        "section": issue.section,
        "field_name": issue.field_name,
        "rule_code": issue.rule.code,
        "severity": issue.severity,
        "message": issue.message,
        "current_value": issue.current_value,
        "previous_value": issue.previous_value,
        "resolved": issue.resolved,
        "created_at": issue.created_at,
    }


class ReportValidationView(APIView):
    def _report(self, request, report_uuid):
        return generics.get_object_or_404(reports_for_user(request.user), uuid=report_uuid)

    def get(self, request, report_uuid):
        report = self._report(request, report_uuid)
        issues = report.quality_issues.select_related("rule").filter(resolved=False).order_by("-severity", "section", "created_at")
        return Response({"report": ReportSerializer(report, context={"request": request}).data, "issues": [quality_issue_payload(issue) for issue in issues]})

    @transaction.atomic
    def post(self, request, report_uuid):
        report = self._report(request, report_uuid)
        if not report.is_editable or not user_has_any_role(request.user, REPORT_AUTHOR_ROLE_CODES):
            return Response({"code": "permission_denied", "detail": "Only an assigned report author can validate an editable report."}, status=403)
        issues = validate_report(report).select_related("rule").order_by("-severity", "section", "created_at")
        report.refresh_from_db()
        return Response({"report": ReportSerializer(report, context={"request": request}).data, "issues": [quality_issue_payload(issue) for issue in issues]})


class ReportDeclarationView(APIView):
    @transaction.atomic
    def post(self, request, report_uuid):
        report = generics.get_object_or_404(reports_for_user(request.user), uuid=report_uuid)
        if not report.is_editable or not user_has_any_role(request.user, REPORT_AUTHOR_ROLE_CODES):
            return Response({"code": "permission_denied", "detail": "This declaration cannot be changed."}, status=403)
        if request.data.get("acknowledged") is not True:
            return Response({"code": "validation_error", "detail": "The final declaration must be acknowledged."}, status=400)
        declaration, _ = FinalDeclaration.objects.update_or_create(
            report=report,
            defaults={"declared_by": request.user, "declaration_text": "I declare this report complete and accurate to the best of my knowledge.", "acknowledged": True},
        )
        recalculate_report_progress(report)
        return Response({"acknowledged": declaration.acknowledged, "declared_at": declaration.declared_at})


class ReportWorkflowView(APIView):
    @transaction.atomic
    def post(self, request, report_uuid, action):
        report = generics.get_object_or_404(reports_for_user(request.user), uuid=report_uuid)
        if action not in available_actions(report, request.user):
            return Response({"code": "permission_denied", "detail": "That workflow action is not available."}, status=403)
        try:
            transition_report(
                report=report, user=request.user, action=action,
                comment=request.data.get("comment", ""),
                acknowledged=request.data.get("acknowledged") is True,
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
        except ValidationError as error:
            return Response({"code": "validation_error", "detail": "; ".join(error.messages)}, status=400)
        report.refresh_from_db()
        return Response(ReportSerializer(report, context={"request": request}).data)


MOBILE_INDICATOR_CODES = (
    "total_population",
    "average_household_size",
    "percentage_water_sources_tested",
    "toilet_coverage",
    "electrification_rate",
    "new_cases_per_1000",
    "project_completion_rate",
    "projects_by_risk_level",
    "decision_completion_rate",
    "overdue_decision_count",
)


class DashboardSummaryView(APIView):
    def get(self, request):
        if not can_view_analytics(request.user):
            return Response({"code": "permission_denied", "detail": "Your role cannot view TNK summaries."}, status=403)
        reports = reports_for_user(request.user).select_related("village__tikina__province", "reporting_period", "previous_report").prefetch_related("section_statuses")
        report_uuid = request.query_params.get("report_uuid")
        if report_uuid:
            report = generics.get_object_or_404(reports, uuid=report_uuid)
        else:
            report = reports.order_by("-reporting_period__year", "-reporting_period__quarter", "-updated_at").first()
        if report is None:
            return Response({"report": None, "indicators": []})
        values = apply_indicator_overrides(
            IndicatorValue.objects.filter(
                village=report.village,
                reporting_period=report.reporting_period,
                indicator__code__in=MOBILE_INDICATOR_CODES,
                indicator__is_active=True,
            ).select_related("indicator", "reporting_period", "village").order_by("indicator__name_en")
        )
        indicators = [
            {
                "uuid": str(value.uuid),
                "code": value.indicator.code,
                "name_en": value.indicator.name_en,
                "name_fj": value.indicator.name_fj,
                "value": str(value.authoritative_value) if value.authoritative_value is not None else None,
                "unit": value.indicator.measurement_unit,
                "status": value.calculation_status,
                "quality_rating": value.data_quality_rating,
                "calculated_at": value.calculated_at,
                "breakdown": value.breakdown,
            }
            for value in values
        ]
        return Response({
            "report": ReportSerializer(report, context={"request": request}).data,
            "location": {
                "village_uuid": str(report.village.uuid),
                "village": report.village.name_en,
                "village_name_en": report.village.name_en,
                "village_name_fj": report.village.name_fj,
                "tikina": report.village.tikina.name_en,
                "tikina_name_en": report.village.tikina.name_en,
                "tikina_name_fj": report.village.tikina.name_fj,
                "province": report.village.tikina.province.name_en,
                "province_name_en": report.village.tikina.province.name_en,
                "province_name_fj": report.village.tikina.province.name_fj,
            },
            "reporting_period": {
                "uuid": str(report.reporting_period.uuid),
                "label": str(report.reporting_period),
                "year": report.reporting_period.year,
                "quarter": report.reporting_period.quarter,
            },
            "pending_validation_issues": report.quality_issues.filter(resolved=False).count(),
            "indicators": indicators,
        })
