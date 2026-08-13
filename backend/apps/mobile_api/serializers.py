from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import UserLocationAssignment
from apps.accounts.permissions import REPORT_AUTHOR_ROLE_CODES, user_has_any_role
from apps.locations.models import Village
from apps.reporting.models import ReportingPeriod, ReportSectionStatus, TNKReport
from apps.reporting.services.report_creation import create_report
from apps.workflow.services import available_actions

from .models import MobileDevice
from .versioning import app_version_policy, parse_app_version


class DeviceLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    device_identifier = serializers.UUIDField()
    platform = serializers.ChoiceField(choices=MobileDevice.Platform.choices)
    app_version = serializers.CharField(max_length=40)
    device_name = serializers.CharField(max_length=120, allow_blank=True, required=False)

    def validate(self, attrs):
        if parse_app_version(attrs["app_version"]) is None:
            raise serializers.ValidationError({"app_version": "Use semantic version format such as 1.2.3 or 1.2.3+45."})
        request = self.context.get("request")
        user = authenticate(request=request, username=attrs["username"], password=attrs["password"])
        if user is None or not user.is_active:
            raise serializers.ValidationError({"credentials": "Unable to sign in with the supplied credentials."})
        device, _ = MobileDevice.objects.update_or_create(
            user=user,
            device_identifier=attrs["device_identifier"],
            defaults={
                "platform": attrs["platform"],
                "app_version": attrs["app_version"],
                "device_name": attrs.get("device_name", ""),
            },
        )
        if not device.is_active or device.revoked_at is not None:
            raise serializers.ValidationError({"device": "This mobile device has been revoked."})
        refresh = RefreshToken.for_user(user)
        refresh["device_uuid"] = str(device.uuid)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "device_uuid": device.uuid,
            "version_policy": app_version_policy(device.app_version),
        }


class VersionPolicySerializer(serializers.Serializer):
    minimum_supported_version = serializers.CharField()
    latest_version = serializers.CharField()
    force_upgrade = serializers.BooleanField()
    update_available = serializers.BooleanField()


class DeviceLoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    device_uuid = serializers.UUIDField()
    version_policy = VersionPolicySerializer()


class DeviceRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        token = RefreshToken(attrs["refresh"])
        device_uuid = token.get("device_uuid")
        if not device_uuid or not MobileDevice.objects.filter(uuid=device_uuid, is_active=True, revoked_at__isnull=True).exists():
            raise serializers.ValidationError({"device": "This mobile device has been revoked."})
        data = super().validate(attrs)
        if "refresh" in data:
            rotated = RefreshToken(data["refresh"])
            rotated["device_uuid"] = device_uuid
            data["refresh"] = str(rotated)
            data["access"] = str(rotated.access_token)
        return data


class LocationAssignmentSerializer(serializers.ModelSerializer):
    level = serializers.SerializerMethodField()
    location_uuid = serializers.SerializerMethodField()
    name_en = serializers.SerializerMethodField()
    name_fj = serializers.SerializerMethodField()

    class Meta:
        model = UserLocationAssignment
        fields = ("uuid", "level", "location_uuid", "name_en", "name_fj")

    def _location(self, obj):
        return obj.village or obj.tikina or obj.province

    def get_level(self, obj):
        return "village" if obj.village_id else "tikina" if obj.tikina_id else "province"

    def get_location_uuid(self, obj):
        return self._location(obj).uuid

    def get_name_en(self, obj):
        return self._location(obj).name_en

    def get_name_fj(self, obj):
        return self._location(obj).name_fj


class VillageSerializer(serializers.ModelSerializer):
    tikina_uuid = serializers.UUIDField(source="tikina.uuid", read_only=True)
    tikina_name_en = serializers.CharField(source="tikina.name_en", read_only=True)
    province_uuid = serializers.UUIDField(source="tikina.province.uuid", read_only=True)
    province_name_en = serializers.CharField(source="tikina.province.name_en", read_only=True)

    class Meta:
        model = Village
        fields = ("uuid", "code", "name_en", "name_fj", "tikina_uuid", "tikina_name_en", "province_uuid", "province_name_en", "updated_at", "record_version")


class ReportingPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportingPeriod
        fields = ("uuid", "year", "quarter", "start_date", "end_date", "submission_due_date", "is_open", "is_locked", "updated_at")


class ReportSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSectionStatus
        fields = ("section_code", "status", "completion_percentage", "issue_count", "confirmed_unchanged", "last_updated_at")


class ReportSerializer(serializers.ModelSerializer):
    village_uuid = serializers.UUIDField(source="village.uuid", read_only=True)
    reporting_period_uuid = serializers.UUIDField(source="reporting_period.uuid", read_only=True)
    previous_report_uuid = serializers.UUIDField(source="previous_report.uuid", read_only=True, allow_null=True)
    sections = ReportSectionSerializer(source="section_statuses", many=True, read_only=True)
    workflow_actions = serializers.SerializerMethodField()
    returned_review = serializers.SerializerMethodField()

    class Meta:
        model = TNKReport
        fields = ("uuid", "village_uuid", "reporting_period_uuid", "previous_report_uuid", "status", "completeness_percentage", "data_quality_score", "overall_risk_level", "record_version", "created_at", "updated_at", "sections", "workflow_actions", "returned_review")

    def get_workflow_actions(self, obj):
        request = self.context.get("request")
        return available_actions(obj, request.user) if request else []

    def get_returned_review(self, obj):
        if obj.status != TNKReport.Status.RETURNED_TO_VILLAGE:
            return None
        action = obj.approval_actions.filter(action_type="return").order_by("-acted_at").first()
        if action is None:
            return None
        affected = list(obj.section_statuses.filter(status=ReportSectionStatus.Status.NEEDS_ATTENTION).values_list("section_code", flat=True))
        return {
            "reviewer": action.user_full_name,
            "returned_at": action.acted_at,
            "comment": action.comment,
            "affected_sections": affected,
        }


class ReportCreateSerializer(serializers.Serializer):
    village_uuid = serializers.UUIDField()
    reporting_period_uuid = serializers.UUIDField()

    def validate(self, attrs):
        user = self.context["request"].user
        if not user_has_any_role(user, REPORT_AUTHOR_ROLE_CODES):
            raise serializers.ValidationError({"role": "Your role cannot create TNK reports."})
        try:
            attrs["village"] = Village.objects.get(uuid=attrs.pop("village_uuid"))
            attrs["reporting_period"] = ReportingPeriod.objects.get(uuid=attrs.pop("reporting_period_uuid"))
        except (Village.DoesNotExist, ReportingPeriod.DoesNotExist):
            raise serializers.ValidationError({"resource": "Village or reporting period was not found."}) from None
        return attrs

    def create(self, validated_data):
        return create_report(prepared_by=self.context["request"].user, **validated_data)
