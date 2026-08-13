from datetime import date
from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TransactionTestCase, override_settings
from django.urls import reverse

from apps.accounts.models import Role, User, UserLocationAssignment, UserRoleAssignment
from apps.analytics.exports import csv_export
from apps.core.security import (
    can_export_record,
    can_view_health_detail,
    can_view_household_detail,
    can_view_record,
    can_view_safety_detail,
    can_view_section,
    permitted_section_codes,
)
from apps.documents.models import EvidenceDocument, EvidenceLink
from apps.locations.models import Province, Tikina, Village
from apps.population.models import AgeGroup, Household
from apps.reporting.models import ReportingPeriod, TNKReport
from apps.reporting.services import create_report
from apps.wellbeing.models import CommunitySafetyIncident, HealthCondition, HealthConditionSnapshot, OffenceType


class ConfidentialityPolicyTests(TransactionTestCase):
    def setUp(self):
        self.province = Province.objects.create(code="SEC", name_en="Security Province")
        self.tikina = Tikina.objects.create(province=self.province, code="ST", name_en="Security Tikina")
        self.village = Village.objects.create(tikina=self.tikina, code="SV1", name_en="Security Village One")
        self.other_village = Village.objects.create(tikina=self.tikina, code="SV2", name_en="Security Village Two")
        self.period = ReportingPeriod.objects.create(
            year=2026,
            quarter=2,
            start_date=date(2026, 4, 1),
            end_date=date(2026, 6, 30),
            submission_due_date=date(2026, 12, 31),
            is_open=True,
        )
        self.users = {
            "system": self.make_user("security-system", Role.Codes.SYSTEM_ADMIN, province=self.province),
            "provincial": self.make_user("security-provincial", Role.Codes.PROVINCIAL_ADMIN, province=self.province),
            "roko": self.make_user("security-roko", Role.Codes.ROKO_TUI, province=self.province),
            "veivuke": self.make_user("security-veivuke", Role.Codes.ROKO_VEIVUKE, tikina=self.tikina),
            "mata": self.make_user("security-mata", Role.Codes.MATA_NI_TIKINA, tikina=self.tikina),
            "tnk": self.make_user("security-tnk", Role.Codes.TURAGA_NI_KORO, village=self.village),
            "assistant": self.make_user("security-assistant", Role.Codes.VILLAGE_DATA_ASSISTANT, village=self.village),
            "nurse": self.make_user("security-nurse", Role.Codes.VILLAGE_NURSE, village=self.village),
            "project": self.make_user("security-project", Role.Codes.PROJECT_OFFICER, village=self.village),
            "analyst": self.make_user("security-analyst", Role.Codes.READ_ONLY_ANALYST, province=self.province),
            "auditor": self.make_user("security-auditor", Role.Codes.AUDITOR, province=self.province),
            "other_tnk": self.make_user("security-other-tnk", Role.Codes.TURAGA_NI_KORO, village=self.other_village),
        }
        self.report = create_report(village=self.village, reporting_period=self.period, prepared_by=self.users["tnk"])
        self.age_group = AgeGroup.objects.create(code="SEC-ALL", name_en="All ages", minimum_age=0)
        self.health_condition = HealthCondition.objects.create(code="SEC-H", name_en="Test condition", category="test")
        self.health_snapshot = HealthConditionSnapshot.objects.create(
            report=self.report,
            health_condition=self.health_condition,
            age_group=self.age_group,
            gender="all",
            new_cases=1,
            measurement_date=date(2026, 5, 1),
            data_source="village_nurse",
            collection_method="register",
        )
        offence = OffenceType.objects.create(code="SEC-O", category="test", name_en="Test offence", default_severity="high")
        self.safety_incident = CommunitySafetyIncident.objects.create(
            village=self.village,
            report=self.report,
            offence_type=offence,
            incident_date=date(2026, 5, 2),
            number_of_incidents=1,
            severity="high",
            reported_to_authority=True,
            authority_reported_to="Police",
            measurement_date=date(2026, 5, 2),
            data_source="police_record",
            collection_method="aggregate return",
        )

    def make_user(self, username, role_code, **location):
        user = User.objects.create_user(username=username)
        role, _ = Role.objects.get_or_create(
            code=role_code,
            defaults={"name": Role(code=role_code).get_code_display()},
        )
        UserRoleAssignment.objects.create(user=user, role=role)
        UserLocationAssignment.objects.create(user=user, **location)
        return user

    def make_document(self, *, level, linked_object, title):
        document = EvidenceDocument.objects.create(
            title=title,
            document_type="report",
            file=SimpleUploadedFile(f"{title}.pdf", b"%PDF-1.4 test", content_type="application/pdf"),
            original_filename=f"{title}.pdf",
            file_size=13,
            mime_type="application/pdf",
            checksum="0" * 64,
            confidentiality_level=level,
            uploaded_by=self.users["tnk"],
        )
        EvidenceLink.objects.create(
            document=document,
            content_type=ContentType.objects.get_for_model(linked_object),
            object_id=linked_object.pk,
        )
        return document

    def assert_download_status(self, user, document, expected):
        self.client.force_login(user)
        response = self.client.get(reverse("documents:download", args=(document.uuid,)))
        self.assertEqual(response.status_code, expected)
        response.close()

    def test_role_section_matrix_is_deny_by_default(self):
        full_roles = {"system", "provincial", "roko", "veivuke", "mata", "tnk", "assistant", "auditor"}
        for name in full_roles:
            with self.subTest(role=name):
                self.assertEqual(len(permitted_section_codes(self.users[name])), 17)
        self.assertEqual(permitted_section_codes(self.users["nurse"]), {"village_profile", "health", "disability"})
        self.assertEqual(permitted_section_codes(self.users["project"]), {"village_profile", "ivdp_projects"})
        self.assertEqual(permitted_section_codes(self.users["analyst"]), set())

        no_role = User.objects.create_user(username="security-no-role")
        UserLocationAssignment.objects.create(user=no_role, village=self.village)
        self.assertFalse(can_view_section(no_role, "village_profile"))
        self.client.force_login(no_role)
        self.assertEqual(self.client.get(reverse("analytics:dashboard")).status_code, 403)
        self.assertEqual(self.client.get(reverse("analytics:export", args=("csv",))).status_code, 403)

    def test_nurse_and_project_officer_only_see_their_sections(self):
        self.client.force_login(self.users["nurse"])
        detail = self.client.get(reverse("reporting:detail", args=(self.report.uuid,)))
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(len(detail.context["sections"]), 3)
        health = self.client.get(reverse("reporting:section_update", args=(self.report.uuid, "health")))
        self.assertEqual(health.status_code, 200)
        self.assertContains(health, "Health condition snapshot")
        self.assertNotContains(health, "Community safety incident")
        self.assertEqual(self.client.get(reverse("reporting:section_update", args=(self.report.uuid, "population_households"))).status_code, 403)

        self.client.force_login(self.users["project"])
        self.assertEqual(self.client.get(reverse("reporting:section_update", args=(self.report.uuid, "ivdp_projects"))).status_code, 200)
        self.assertEqual(self.client.get(reverse("reporting:section_update", args=(self.report.uuid, "health"))).status_code, 403)

    def test_health_household_and_safety_policy_combines_role_and_location(self):
        household = Household.objects.create(
            household_code="SEC-HH",
            village=self.village,
            household_head_name="Sensitive Household Name",
            household_size=3,
            effective_from=date(2026, 4, 1),
        )
        self.assertTrue(can_view_record(self.users["nurse"], self.health_snapshot))
        self.assertTrue(can_view_health_detail(self.users["nurse"], self.village))
        self.assertFalse(can_view_record(self.users["nurse"], household))
        self.assertFalse(can_view_household_detail(self.users["nurse"], self.village))
        self.assertFalse(can_view_record(self.users["nurse"], self.safety_incident))
        self.assertFalse(can_view_safety_detail(self.users["nurse"], self.village))
        self.assertTrue(can_view_record(self.users["tnk"], self.safety_incident))
        self.assertFalse(can_view_record(self.users["other_tnk"], self.health_snapshot))
        self.assertFalse(can_export_record(self.users["system"], self.health_snapshot))

    def test_evidence_checks_level_linked_object_location_and_report_status(self):
        with override_settings(MEDIA_ROOT=settings.BASE_DIR / "test_media"):
            report_document = self.make_document(level="highly_restricted", linked_object=self.report, title="report-secret")
            health_document = self.make_document(level="highly_restricted", linked_object=self.health_snapshot, title="health-secret")
            safety_document = self.make_document(level="highly_restricted", linked_object=self.safety_incident, title="safety-secret")

            self.assert_download_status(self.users["tnk"], report_document, 200)
            self.assert_download_status(self.users["other_tnk"], report_document, 403)
            self.assert_download_status(self.users["analyst"], report_document, 403)
            self.assert_download_status(self.users["nurse"], report_document, 403)
            self.assert_download_status(self.users["nurse"], health_document, 200)
            self.assert_download_status(self.users["project"], health_document, 403)
            self.assert_download_status(self.users["nurse"], safety_document, 403)

            self.assert_download_status(self.users["mata"], report_document, 403)
            TNKReport.objects.filter(pk=self.report.pk).update(status=TNKReport.Status.SUBMITTED)
            self.report.refresh_from_db()
            self.assert_download_status(self.users["mata"], report_document, 200)

    def test_analyst_remains_aggregate_only_and_exports_exclude_sensitive_values(self):
        Household.objects.create(
            household_code="SEC-EXPORT",
            village=self.village,
            household_head_name="Never Export This Person",
            household_size=2,
            effective_from=date(2026, 4, 1),
        )
        self.client.force_login(self.users["analyst"])
        self.assertEqual(self.client.get(reverse("analytics:dashboard")).status_code, 200)
        export = self.client.get(reverse("analytics:export", args=("csv",)))
        self.assertEqual(export.status_code, 200)
        self.assertNotContains(export, "Never Export This Person")
        self.assertNotContains(export, "Test condition")
        self.assertEqual(self.client.get(reverse("reporting:detail", args=(self.report.uuid,))).status_code, 403)

    def test_export_service_reapplies_role_and_location_policy(self):
        other_report = create_report(
            village=self.other_village,
            reporting_period=self.period,
            prepared_by=self.users["other_tnk"],
        )
        response = csv_export(self.users["tnk"], [self.report, other_report], {}, "scope test")
        body = response.content.decode()
        self.assertIn(self.village.name_en, body)
        self.assertNotIn(self.other_village.name_en, body)

        no_role = User.objects.create_user(username="security-direct-export-no-role")
        UserLocationAssignment.objects.create(user=no_role, province=self.province)
        with self.assertRaises(PermissionDenied):
            csv_export(no_role, [self.report], {}, "denied")

    def test_sensitive_admin_is_limited_to_trusted_roles(self):
        nurse_request = RequestFactory().get("/admin/")
        nurse_request.user = self.users["nurse"]
        health_admin = admin.site._registry[HealthConditionSnapshot]
        evidence_admin = admin.site._registry[EvidenceDocument]
        self.assertFalse(health_admin.has_module_permission(nurse_request))
        self.assertFalse(evidence_admin.has_module_permission(nurse_request))

        system = self.users["system"]
        system.is_staff = True
        system.is_superuser = True
        system.save(update_fields=("is_staff", "is_superuser"))
        system_request = RequestFactory().get("/admin/")
        system_request.user = system
        self.assertTrue(health_admin.has_module_permission(system_request))
        self.assertTrue(evidence_admin.has_module_permission(system_request))
