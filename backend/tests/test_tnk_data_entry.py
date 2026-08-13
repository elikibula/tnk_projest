from datetime import date
from decimal import Decimal

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import Role, User, UserLocationAssignment, UserRoleAssignment
from apps.audit.models import AuditEvent
from apps.documents.models import EvidenceDocument
from apps.locations.models import Province, Tikina, Village
from apps.population.models import AgeGroup, PopulationMovement, PopulationSnapshot
from apps.reporting.forms import SectionStatusForm
from apps.reporting.models import ReportSectionStatus, ReportingPeriod, TNKReport
from apps.reporting.section_entries import entry_queryset
from apps.reporting.section_registry import SECTION_ENTRIES, get_entry_config
from apps.reporting.services import create_report


class TNKDataEntryWorkflowTests(TestCase):
    def setUp(self):
        self.province = Province.objects.create(code="LAU", name_en="Lau")
        self.tikina = Tikina.objects.create(province=self.province, code="LAK", name_en="Lakeba")
        self.village = Village.objects.create(tikina=self.tikina, code="TUB", name_en="Tubou")
        self.other_village = Village.objects.create(tikina=self.tikina, code="OTH", name_en="Other")
        self.user = User.objects.create_user(username="tnk", password="safe-password")
        role = Role.objects.create(code=Role.Codes.TURAGA_NI_KORO, name="Turaga ni Koro")
        UserRoleAssignment.objects.create(user=self.user, role=role)
        UserLocationAssignment.objects.create(user=self.user, village=self.village)
        self.period = ReportingPeriod.objects.create(year=2026, quarter=2, start_date=date(2026, 4, 1), end_date=date(2026, 6, 30), submission_due_date=date(2026, 7, 15), is_open=True)
        self.report = create_report(village=self.village, reporting_period=self.period, prepared_by=self.user)
        self.age_group = AgeGroup.objects.create(code="25_34", name_en="25-34", minimum_age=25, maximum_age=34)
        self.client.force_login(self.user)

    def test_all_substantive_sections_have_entry_workflows(self):
        self.assertEqual(len(SECTION_ENTRIES), 15)
        self.assertGreaterEqual(sum(len(entries) for entries in SECTION_ENTRIES.values()), 40)
        for section_code in SECTION_ENTRIES:
            response = self.client.get(reverse("reporting:section_update", args=(self.report.uuid, section_code)))
            self.assertEqual(response.status_code, 200, section_code)
            self.assertContains(response, "Each record saves independently")

    def test_every_configured_create_form_renders(self):
        for section_code, configs in SECTION_ENTRIES.items():
            for config in configs:
                if not config.allow_create:
                    continue
                with self.subTest(section=section_code, entry=config.key):
                    response = self.client.get(reverse("reporting:entry_create", args=(self.report.uuid, section_code, config.key)))
                    self.assertEqual(response.status_code, 200)
                    self.assertContains(response, "Save record")

    def test_generic_forms_do_not_expose_legacy_direct_file_fields(self):
        unsafe_fields = {"supporting_document", "evidence_document", "verification_document", "plan_document"}
        for configs in SECTION_ENTRIES.values():
            for config in configs:
                self.assertFalse(unsafe_fields.intersection(config.fields), config.key)

    def test_author_cannot_mark_a_section_verified(self):
        form = SectionStatusForm(instance=self.report.section_statuses.first(), initial={"expected_version": 1})
        values = {value for value, _label in form.fields["status"].choices}
        self.assertNotIn(ReportSectionStatus.Status.VERIFIED, values)
        self.assertNotIn("completion_percentage", form.fields)

    def test_confirmed_unchanged_automatically_completes_section(self):
        from apps.reporting.services import update_section_status

        section = self.report.section_statuses.get(section_code=ReportSectionStatus.Section.WATER)
        update_section_status(
            report=self.report,
            section_code=section.section_code,
            status=ReportSectionStatus.Status.IN_PROGRESS,
            confirmed_unchanged=True,
            user=self.user,
            expected_version=1,
        )
        section.refresh_from_db()
        self.report.refresh_from_db()
        self.assertEqual(section.status, ReportSectionStatus.Status.COMPLETE)
        self.assertEqual(section.completion_percentage, 100)
        self.assertEqual(self.report.completeness_percentage, Decimal("5.88"))

    def test_period_scoped_entry_does_not_leak_from_other_quarter(self):
        other_period = ReportingPeriod.objects.create(year=2026, quarter=1, start_date=date(2026, 1, 1), end_date=date(2026, 3, 31), submission_due_date=date(2026, 4, 15), is_open=False)
        current = PopulationMovement.objects.create(village=self.village, reporting_period=self.period, movement_type="birth", movement_date=date(2026, 5, 1), count=1, data_source="physical_count")
        PopulationMovement.objects.create(village=self.village, reporting_period=other_period, movement_type="birth", movement_date=date(2026, 2, 1), count=2, data_source="physical_count")
        queryset = entry_queryset(get_entry_config("population_households", "movement"), self.report)
        self.assertEqual(list(queryset), [current])

    def test_population_entry_binds_report_and_village_server_side(self):
        response = self.client.post(reverse("reporting:entry_create", args=(self.report.uuid, "population_households", "population")), {
            "age_group": self.age_group.pk, "gender": "female", "resident_status": "permanent_resident", "count": 15,
            "measurement_date": "2026-06-30", "measurement_unit": "people", "data_source": "physical_count",
            "collection_method": "household census", "source_reference": "Register 2026 Q2", "verification_status": "unverified",
            "confidence_level": "high", "notes": "",
        })
        self.assertRedirects(response, reverse("reporting:section_update", args=(self.report.uuid, "population_households")))
        snapshot = PopulationSnapshot.objects.get()
        self.assertEqual(snapshot.report, self.report)
        self.assertEqual(snapshot.village, self.village)
        section = self.report.section_statuses.get(section_code="population_households")
        self.assertEqual(section.status, ReportSectionStatus.Status.IN_PROGRESS)
        self.assertEqual(section.last_updated_by, self.user)
        self.assertTrue(AuditEvent.objects.filter(action="report.entry_saved", object_uuid=snapshot.uuid).exists())
        self.report.refresh_from_db()
        self.assertGreater(self.report.completeness_percentage, 0)

    def test_itaukei_language_translates_dynamic_data_entry_form(self):
        self.client.post(reverse("set_language"), {"language": "fj", "next": "/"})
        response = self.client.get(reverse("reporting:entry_create", args=(self.report.uuid, "population_households", "population")))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Iwiliwili ni lewenivanua")
        self.assertContains(response, "Tagane se yalewa")
        self.assertContains(response, "Dau tiko tudei")
        self.assertContains(response, "Maroroya na itukutuku")

    def test_master_person_entry_is_bound_to_assigned_village(self):
        response = self.client.post(reverse("reporting:entry_create", args=(self.report.uuid, "leadership_governance", "person")), {
            "full_name": "Fictional Official", "gender": "male", "date_of_birth": "1980-01-01", "phone": "", "email": "",
            "confidentiality_level": "confidential", "is_active": "on",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.village.people.get().full_name, "Fictional Official")
        self.assertFalse(self.other_village.people.exists())

    def test_user_without_author_role_cannot_open_entry_form(self):
        reviewer = User.objects.create_user(username="reviewer")
        reviewer_role = Role.objects.create(code=Role.Codes.MATA_NI_TIKINA, name="Mata ni Tikina")
        UserRoleAssignment.objects.create(user=reviewer, role=reviewer_role)
        UserLocationAssignment.objects.create(user=reviewer, tikina=self.tikina)
        self.client.force_login(reviewer)
        response = self.client.get(reverse("reporting:entry_create", args=(self.report.uuid, "population_households", "population")))
        self.assertEqual(response.status_code, 403)

    def test_reviewer_cannot_sign_the_village_final_declaration(self):
        reviewer = User.objects.create_user(username="declaration-reviewer")
        reviewer_role = Role.objects.create(code=Role.Codes.MATA_NI_TIKINA, name="Mata ni Tikina")
        UserRoleAssignment.objects.create(user=reviewer, role=reviewer_role)
        UserLocationAssignment.objects.create(user=reviewer, tikina=self.tikina)
        self.client.force_login(reviewer)
        response = self.client.post(reverse("reporting:declare", args=(self.report.uuid,)), {"acknowledged": "on"})
        self.assertEqual(response.status_code, 403)

    def test_submitted_report_rejects_entry_changes(self):
        TNKReport.objects.filter(pk=self.report.pk).update(status=TNKReport.Status.SUBMITTED)
        self.report.refresh_from_db()
        response = self.client.get(reverse("reporting:entry_create", args=(self.report.uuid, "population_households", "population")))
        self.assertEqual(response.status_code, 403)

    @override_settings(MEDIA_ROOT=settings.BASE_DIR / "test_media")
    def test_evidence_upload_is_linked_to_report(self):
        response = self.client.post(reverse("reporting:evidence_upload", args=(self.report.uuid,)), {
            "title": "Population register", "document_type": "register", "description": "Fictional test evidence",
            "confidentiality_level": "restricted", "file": SimpleUploadedFile("register.pdf", b"%PDF-1.4 fictional", content_type="application/pdf"),
        })
        self.assertEqual(response.status_code, 302)
        document = EvidenceDocument.objects.get()
        self.assertEqual(document.links.get().content_object, self.report)
        self.assertEqual(len(document.checksum), 64)
