from datetime import date, datetime
from decimal import Decimal

from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Role, User, UserLocationAssignment, UserRoleAssignment
from apps.audit.models import AuditEvent
from apps.locations.models import Province, Tikina, Village
from apps.reporting.models import ReportingPeriod, ReportSectionStatus, TNKReport
from apps.reporting.selectors import reports_for_user
from apps.reporting.services import create_report, update_section_status


class ReportingPhaseTests(TestCase):
    def setUp(self):
        province = Province.objects.create(code="LAU", name_en="Lau")
        tikina = Tikina.objects.create(province=province, code="LAKEBA", name_en="Lakeba")
        self.village = Village.objects.create(tikina=tikina, code="TUBOU", name_en="Tubou")
        self.other_village = Village.objects.create(tikina=tikina, code="LEVUKA", name_en="Levuka")
        self.user = User.objects.create_user(username="tnk", password="safe-password")
        role = Role.objects.create(code=Role.Codes.TURAGA_NI_KORO, name="Turaga ni Koro")
        UserRoleAssignment.objects.create(user=self.user, role=role)
        UserLocationAssignment.objects.create(user=self.user, village=self.village)
        self.period = ReportingPeriod.objects.create(year=2026, quarter=1, start_date=date(2026, 1, 1), end_date=date(2026, 3, 31), submission_due_date=date(2026, 4, 15), is_open=True)

    def test_invalid_period_values_are_rejected(self):
        invalid = ReportingPeriod(year=4, quarter=5, start_date=date(2026, 4, 1), end_date=date(2026, 3, 31), submission_due_date=date(2026, 3, 1))
        with self.assertRaises(ValidationError):
            invalid.full_clean()

    def test_create_report_creates_sections_and_audit(self):
        report = create_report(village=self.village, reporting_period=self.period, prepared_by=self.user)
        self.assertEqual(report.section_statuses.count(), 17)
        self.assertEqual(report.status, TNKReport.Status.DRAFT)
        self.assertTrue(AuditEvent.objects.filter(action="report.created", object_uuid=report.uuid).exists())

    def test_only_one_report_per_village_and_period(self):
        create_report(village=self.village, reporting_period=self.period, prepared_by=self.user)
        with self.assertRaises(ValidationError):
            create_report(village=self.village, reporting_period=self.period, prepared_by=self.user)

    def test_unassigned_village_cannot_be_used(self):
        with self.assertRaises(PermissionDenied):
            create_report(village=self.other_village, reporting_period=self.period, prepared_by=self.user)

    def test_latest_approved_report_is_selected_for_comparison(self):
        previous_period = ReportingPeriod.objects.create(year=2025, quarter=4, start_date=date(2025, 10, 1), end_date=date(2025, 12, 31), submission_due_date=date(2026, 1, 15))
        previous = TNKReport.objects.create(village=self.village, reporting_period=previous_period, prepared_by=self.user, collection_started_at=timezone.make_aware(datetime(2025, 10, 1)), status=TNKReport.Status.APPROVED)
        report = create_report(village=self.village, reporting_period=self.period, prepared_by=self.user)
        self.assertEqual(report.previous_report, previous)

    def test_archived_official_report_is_selected_but_draft_is_ignored(self):
        q3 = ReportingPeriod.objects.create(year=2025, quarter=3, start_date=date(2025, 7, 1), end_date=date(2025, 9, 30), submission_due_date=date(2025, 10, 15))
        q4 = ReportingPeriod.objects.create(year=2025, quarter=4, start_date=date(2025, 10, 1), end_date=date(2025, 12, 31), submission_due_date=date(2026, 1, 15))
        archived = TNKReport.objects.create(village=self.village, reporting_period=q3, prepared_by=self.user, collection_started_at=timezone.make_aware(datetime(2025, 7, 1)), status=TNKReport.Status.ARCHIVED)
        TNKReport.objects.create(village=self.village, reporting_period=q4, prepared_by=self.user, collection_started_at=timezone.make_aware(datetime(2025, 10, 1)), status=TNKReport.Status.DRAFT)
        report = create_report(village=self.village, reporting_period=self.period, prepared_by=self.user)
        self.assertEqual(report.previous_report, archived)

    def test_missing_previous_official_report_is_handled(self):
        report = create_report(village=self.village, reporting_period=self.period, prepared_by=self.user)
        self.assertIsNone(report.previous_report)

    def test_section_save_updates_completion_and_version(self):
        report = create_report(village=self.village, reporting_period=self.period, prepared_by=self.user)
        update_section_status(report=report, section_code=ReportSectionStatus.Section.WATER, status=ReportSectionStatus.Status.COMPLETE, completion_percentage=Decimal("100"), confirmed_unchanged=False, user=self.user, expected_version=1)
        report.refresh_from_db()
        self.assertEqual(report.record_version, 2)
        self.assertEqual(report.completeness_percentage, Decimal("5.88"))

    def test_stale_section_save_is_rejected(self):
        report = create_report(village=self.village, reporting_period=self.period, prepared_by=self.user)
        update_section_status(report=report, section_code=ReportSectionStatus.Section.WATER, status=ReportSectionStatus.Status.IN_PROGRESS, completion_percentage=Decimal("50"), confirmed_unchanged=False, user=self.user, expected_version=1)
        with self.assertRaises(ValidationError):
            update_section_status(report=report, section_code=ReportSectionStatus.Section.HEALTH, status=ReportSectionStatus.Status.IN_PROGRESS, completion_percentage=Decimal("10"), confirmed_unchanged=False, user=self.user, expected_version=1)

    def test_approved_report_cannot_be_deleted(self):
        report = create_report(village=self.village, reporting_period=self.period, prepared_by=self.user)
        TNKReport.objects.filter(pk=report.pk).update(status=TNKReport.Status.APPROVED)
        report.refresh_from_db()
        with self.assertRaises(ValidationError):
            report.delete()
        with self.assertRaises(ValidationError):
            TNKReport.objects.filter(pk=report.pk).delete()

    def test_archived_report_cannot_be_deleted(self):
        report = create_report(village=self.village, reporting_period=self.period, prepared_by=self.user)
        TNKReport.objects.filter(pk=report.pk).update(status=TNKReport.Status.ARCHIVED)
        report.refresh_from_db()
        with self.assertRaises(ValidationError):
            report.delete()

    def test_dashboard_and_detail_are_location_scoped(self):
        report = create_report(village=self.village, reporting_period=self.period, prepared_by=self.user)
        outsider = User.objects.create_user(username="outsider", password="safe-password")
        UserLocationAssignment.objects.create(user=outsider, village=self.other_village)
        self.assertFalse(reports_for_user(outsider).filter(pk=report.pk).exists())
        self.client.force_login(outsider)
        response = self.client.get(reverse("reporting:detail", args=(report.uuid,)))
        self.assertEqual(response.status_code, 403)

    def test_create_view_works_for_authorised_user(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("reporting:create"), {"village": self.village.pk, "reporting_period": self.period.pk})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(TNKReport.objects.count(), 1)
