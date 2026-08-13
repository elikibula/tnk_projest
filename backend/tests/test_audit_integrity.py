from datetime import date
from decimal import Decimal
import io

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from openpyxl import load_workbook

from apps.accounts.models import Role, User, UserLocationAssignment, UserRoleAssignment
from apps.analytics.exports import xlsx_export
from apps.analytics.services import calculate_village_indicators
from apps.audit.models import AuditEvent
from apps.data_quality.models import DataQualityIssue
from apps.data_quality.services import validate_report
from apps.documents.validators import validate_evidence_file
from apps.governance.models import CommitteeMeeting
from apps.infrastructure.models import EnergySnapshot
from apps.locations.models import Province, Tikina, Village
from apps.population.models import AgeGroup, Household, PopulationMovement, PopulationSnapshot
from apps.projects.models import IVDPProject
from apps.reporting.models import ReportingPeriod
from apps.reporting.services import create_report


class AuditIntegrityTests(TestCase):
    def setUp(self):
        self.province = Province.objects.create(code="AUD", name_en="Audit Province")
        self.tikina = Tikina.objects.create(province=self.province, code="A", name_en="Tikina A")
        self.village = Village.objects.create(tikina=self.tikina, code="A1", name_en="Village A1")
        self.user = User.objects.create_user(username="auditor-author")
        role = Role.objects.create(code=Role.Codes.TURAGA_NI_KORO, name="Turaga ni Koro")
        UserRoleAssignment.objects.create(user=self.user, role=role)
        UserLocationAssignment.objects.create(user=self.user, village=self.village)
        self.period = ReportingPeriod.objects.create(year=2026, quarter=2, start_date=date(2026, 4, 1), end_date=date(2026, 6, 30), submission_due_date=date(2026, 7, 15), is_open=True)
        self.report = create_report(village=self.village, reporting_period=self.period, prepared_by=self.user)

    def analytical_defaults(self):
        return {
            "report": self.report,
            "measurement_date": date(2026, 5, 1),
            "data_source": "physical_count",
            "collection_method": "count",
        }

    def test_revalidation_preserves_and_resolves_issue_history(self):
        validate_report(self.report)
        first = DataQualityIssue.objects.get(report=self.report, rule__code="required_sections", resolved=False)
        validate_report(self.report)
        self.assertEqual(DataQualityIssue.objects.filter(report=self.report, rule__code="required_sections").count(), 1)
        self.report.section_statuses.update(status="complete", completion_percentage=100)
        validate_report(self.report)
        first.refresh_from_db()
        self.assertTrue(first.resolved)
        self.assertIsNotNone(first.resolved_at)

    def test_household_and_attendance_breakdowns_are_validated(self):
        household = Household(village=self.village, household_code="H1", household_head_name="Head", household_size=2, male_count=2, female_count=1, effective_from=date(2026, 1, 1))
        with self.assertRaises(ValidationError):
            household.full_clean()
        meeting = CommitteeMeeting(total_attendance=5, youth_attendance=6)
        with self.assertRaises(ValidationError):
            meeting.clean()

    def test_energy_bounds_and_project_dates_are_validated(self):
        energy = EnergySnapshot(average_hours_available_per_day=Decimal("25"), **self.analytical_defaults())
        with self.assertRaises(ValidationError):
            energy.full_clean(exclude=("energy_source", "primary_or_backup"))
        project = IVDPProject(village=self.village, project_code="P1", project_name="Project", project_category="water", problem_being_addressed="Need", priority="high", project_status="active", planned_start_date=date(2026, 5, 2), planned_end_date=date(2026, 5, 1), estimated_budget=Decimal("-1"))
        with self.assertRaises(ValidationError):
            project.full_clean()

    def test_invalid_dashboard_and_export_filters_do_not_crash(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("analytics:dashboard"), {"year": "not-a-year", "quarter": "5", "village": "x", "status": "invented"})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("analytics:export", args=("csv",)), {"year": "not-a-year"})
        self.assertEqual(response.status_code, 200)

    def test_xlsx_keeps_year_quarter_and_scores_numeric(self):
        self.report.data_quality_score = Decimal("88.25")
        self.report.save(update_fields=("data_quality_score", "updated_at"))
        response = xlsx_export(self.user, [self.report], {}, "audit")
        sheet = load_workbook(io.BytesIO(response.content))["Reports"]
        self.assertEqual(sheet["D2"].value, 2026)
        self.assertEqual(sheet["E2"].value, 2)
        self.assertEqual(sheet["I2"].value, 0)
        self.assertEqual(sheet["J2"].value, 88.25)
        for cell in ("D2", "E2", "I2", "J2"):
            self.assertEqual(sheet[cell].data_type, "n")

    def test_role_and_location_assignment_changes_are_audited(self):
        self.assertTrue(AuditEvent.objects.filter(action="role_assignment.created").exists())
        assignment = self.user.location_assignments.get()
        assignment.is_active = False
        assignment.save(update_fields=("is_active",))
        self.assertTrue(AuditEvent.objects.filter(action="location_assignment.changed", object_uuid=assignment.uuid).exists())

    def test_evidence_content_must_match_extension(self):
        disguised = SimpleUploadedFile("evidence.pdf", b"This is not a PDF", content_type="application/pdf")
        with self.assertRaises(ValidationError):
            validate_evidence_file(disguised)
        valid = SimpleUploadedFile("evidence.pdf", b"%PDF-1.4\nvalid", content_type="application/pdf")
        validate_evidence_file(valid)

    def test_read_only_analyst_gets_aggregates_not_detailed_records(self):
        analyst = User.objects.create_user(username="analyst")
        role = Role.objects.create(code=Role.Codes.READ_ONLY_ANALYST, name="Read-only Analyst")
        UserRoleAssignment.objects.create(user=analyst, role=role)
        UserLocationAssignment.objects.create(user=analyst, village=self.village)
        self.client.force_login(analyst)
        self.assertEqual(self.client.get(reverse("analytics:dashboard")).status_code, 200)
        self.assertEqual(self.client.get(reverse("reporting:detail", args=(self.report.uuid,))).status_code, 403)

    def test_non_author_cannot_trigger_mutating_validation_view(self):
        auditor = User.objects.create_user(username="readonly-auditor")
        role = Role.objects.create(code=Role.Codes.AUDITOR, name="Auditor")
        UserRoleAssignment.objects.create(user=auditor, role=role)
        UserLocationAssignment.objects.create(user=auditor, village=self.village)
        self.client.force_login(auditor)
        response = self.client.post(reverse("reporting:validate", args=(self.report.uuid,)))
        self.assertEqual(response.status_code, 403)
        self.assertFalse(DataQualityIssue.objects.filter(report=self.report).exists())

    def test_implemented_population_indicators_use_verified_aggregates(self):
        age = AgeGroup.objects.create(code="ALL", name_en="All ages", minimum_age=0)
        PopulationSnapshot.objects.create(
            village=self.village,
            age_group=age,
            gender="all",
            resident_status="permanent_resident",
            count=10,
            verification_status="verified",
            **self.analytical_defaults(),
        )
        PopulationMovement.objects.create(village=self.village, reporting_period=self.period, movement_type="moved_in", movement_date=date(2026, 5, 1), count=4, data_source="village_register")
        PopulationMovement.objects.create(village=self.village, reporting_period=self.period, movement_type="moved_out", movement_date=date(2026, 5, 2), count=1, data_source="village_register")
        values = {value.indicator.code: value.value for value in calculate_village_indicators(self.report)}
        self.assertEqual(values["total_population"], Decimal("10"))
        self.assertIsNone(values["average_household_size"])
        self.assertEqual(values["net_migration"], Decimal("3"))
        for number in range(2):
            Household.objects.create(village=self.village, household_code=f"H{number}", household_head_name="Head", effective_from=date(2026, 1, 1))
        values = {value.indicator.code: value.value for value in calculate_village_indicators(self.report)}
        self.assertEqual(values["average_household_size"], Decimal("5"))
