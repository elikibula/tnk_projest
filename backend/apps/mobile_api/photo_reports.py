"""Role-scoped Photo Reports API backed by the website's security rules."""
from pathlib import Path

from django.contrib.contenttypes.models import ContentType
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView

from apps.accounts.permissions import PHOTO_REPORT_ROLE_CODES, user_has_any_role
from apps.core.security import can_view_document, can_view_report
from apps.core.security.confidentiality import PRE_SUBMISSION_EVIDENCE_ROLES, PRE_SUBMISSION_STATUSES
from apps.documents.models import EvidenceDocument, RecordPhoto
from apps.documents.photos import PHOTO_SECTIONS
from apps.reporting.models import ReportSectionStatus, TNKReport
from apps.reporting.section_registry import get_entry_config
from apps.reporting.selectors import reports_for_user

from .exploration import MobilePage
from .serializers import ReportSerializer


def _require_photo_reports(user):
    if not user_has_any_role(user, PHOTO_REPORT_ROLE_CODES):
        raise PermissionDenied("Photo Reports is available to Roko Tui Veivuke and higher roles.")


class PhotoReportQuery(serializers.Serializer):
    province = serializers.UUIDField(required=False)
    tikina = serializers.UUIDField(required=False)
    village = serializers.UUIDField(required=False)
    year = serializers.IntegerField(required=False, min_value=2000, max_value=2200)
    quarter = serializers.IntegerField(required=False, min_value=1, max_value=4)
    status = serializers.ChoiceField(choices=TNKReport.Status.choices, required=False)


class PhotoGalleryQuery(serializers.Serializer):
    area = serializers.ChoiceField(
        required=False,
        choices=tuple(code for code, _ in ReportSectionStatus.Section.choices if code in PHOTO_SECTIONS) + ("general",),
    )
    stage = serializers.ChoiceField(required=False, choices=tuple(value for value, _ in RecordPhoto.STAGES) + ("unspecified",))


def _documents_for(user, report):
    documents = EvidenceDocument.objects.filter(
        links__content_type=ContentType.objects.get_for_model(report),
        links__object_id=report.pk,
    ).select_related("record_photo").order_by("captured_at", "uploaded_at", "pk").distinct()
    if report.status in PRE_SUBMISSION_STATUSES and not user_has_any_role(user, PRE_SUBMISSION_EVIDENCE_ROLES):
        return documents.none()
    return documents


def _photo_rows(request, report):
    labels = dict(ReportSectionStatus.Section.choices)
    rows = []
    for document in _documents_for(request.user, report):
        if Path(document.file.name).suffix.lower() not in {".jpg", ".jpeg", ".png"} or not can_view_document(request.user, document):
            continue
        photo = getattr(document, "record_photo", None)
        if photo and photo.report_id != report.pk:
            continue
        area = photo.section_code if photo else "general"
        config = get_entry_config(photo.section_code, photo.entry_key) if photo else None
        rows.append({
            "uuid": str(document.uuid),
            "title": document.title,
            "description": document.description,
            "mime_type": document.mime_type,
            "captured_at": document.captured_at,
            "uploaded_at": document.uploaded_at,
            "confidentiality_level": document.confidentiality_level,
            "latitude": document.latitude,
            "longitude": document.longitude,
            "location_accuracy_metres": document.location_accuracy_metres,
            "area": area,
            "area_label": labels.get(area, "General report evidence"),
            "stage": photo.stage if photo else "unspecified",
            "stage_label": photo.get_stage_display() if photo else "Not specified",
            "record_label": config.display_label if config else "Report evidence",
            "record_identifier": photo.record_identifier if photo else "",
            "image_url": request.build_absolute_uri(reverse("mobile_api:photo-report-image", args=(document.uuid,))),
        })
    return rows


class PhotoReportListView(APIView):
    def get(self, request):
        _require_photo_reports(request.user)
        query = PhotoReportQuery(data=request.query_params)
        query.is_valid(raise_exception=True)
        reports = reports_for_user(request.user).select_related("village__tikina__province", "reporting_period").prefetch_related("section_statuses", "approval_actions")
        lookups = {
            "province": "village__tikina__province__uuid",
            "tikina": "village__tikina__uuid",
            "village": "village__uuid",
            "year": "reporting_period__year",
            "quarter": "reporting_period__quarter",
            "status": "status",
        }
        for field, lookup in lookups.items():
            value = query.validated_data.get(field)
            if value is not None:
                reports = reports.filter(**{lookup: value})
        reports = reports.order_by("-reporting_period__year", "-reporting_period__quarter", "village__name_en", "pk")
        page = MobilePage()
        items = page.paginate_queryset(reports, request)
        return page.get_paginated_response(ReportSerializer(items, many=True, context={"request": request}).data)


class PhotoReportDetailView(APIView):
    def get(self, request, report_uuid):
        _require_photo_reports(request.user)
        report = get_object_or_404(reports_for_user(request.user), uuid=report_uuid)
        if not can_view_report(request.user, report):
            raise PermissionDenied("You cannot view this report.")
        query = PhotoGalleryQuery(data=request.query_params)
        query.is_valid(raise_exception=True)
        all_rows = _photo_rows(request, report)
        rows = [row for row in all_rows if (not query.validated_data.get("area") or row["area"] == query.validated_data["area"]) and (not query.validated_data.get("stage") or row["stage"] == query.validated_data["stage"])]
        order = {"before": 0, "progress": 1, "after": 2, "observation": 3, "unspecified": 4}
        rows.sort(key=lambda row: (order.get(row["stage"], 4), row["captured_at"] or row["uploaded_at"]))
        page = MobilePage()
        items = page.paginate_queryset(rows, request)
        response = page.get_paginated_response(items)
        response.data["total_photos"] = len(all_rows)
        response.data["report"] = ReportSerializer(report, context={"request": request}).data
        return response


class PhotoReportImageView(APIView):
    def get(self, request, document_uuid):
        _require_photo_reports(request.user)
        document = get_object_or_404(EvidenceDocument, uuid=document_uuid)
        links = document.links.filter(content_type=ContentType.objects.get_for_model(TNKReport)).select_related()
        report_ids = links.values_list("object_id", flat=True)
        report = get_object_or_404(reports_for_user(request.user), pk__in=report_ids)
        if not can_view_report(request.user, report) or not can_view_document(request.user, document):
            raise PermissionDenied("You cannot view this photo.")
        if report.status in PRE_SUBMISSION_STATUSES and not user_has_any_role(request.user, PRE_SUBMISSION_EVIDENCE_ROLES):
            raise PermissionDenied("This evidence is not available before submission.")
        if Path(document.file.name).suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            raise PermissionDenied("This document is not a gallery image.")
        response = FileResponse(document.file.open("rb"), content_type=document.mime_type or "application/octet-stream")
        response["Cache-Control"] = "private, no-store"
        response["Content-Disposition"] = f'inline; filename="{Path(document.original_filename or document.file.name).name}"'
        return response
