from datetime import date
import io
import zipfile

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import Role, User, UserLocationAssignment, UserRoleAssignment
from apps.analytics.models import DataExportAudit
from apps.analytics.models import IndicatorValue
from apps.analytics.exports import safe_spreadsheet_value
from apps.data_quality.services import validate_report
from apps.documents.models import EvidenceDocument, EvidenceLink
from apps.locations.models import Province, Tikina, Village
from apps.reporting.models import ReportSectionStatus, ReportingPeriod, TNKReport
from apps.reporting.services import create_report
from apps.workflow.models import FinalDeclaration
from apps.workflow.services import transition_report
from django.conf import settings


class WorkflowQualityExportTests(TestCase):
    def setUp(self):
        self.province = Province.objects.create(code="LAU", name_en="Lau")
        self.tikina = Tikina.objects.create(province=self.province, code="LAK", name_en="Lakeba")
        self.village = Village.objects.create(tikina=self.tikina, code="TUB", name_en="Tubou")
        self.period = ReportingPeriod.objects.create(year=2026, quarter=1, start_date=date(2026, 1, 1), end_date=date(2026, 3, 31), submission_due_date=date(2026, 12, 31), is_open=True)
        self.author = self.make_user("author", Role.Codes.TURAGA_NI_KORO, village=self.village)
        self.reviewer = self.make_user("reviewer", Role.Codes.MATA_NI_TIKINA, tikina=self.tikina)
        self.approver = self.make_user("approver", Role.Codes.ROKO_TUI, province=self.province)
        self.report = create_report(village=self.village, reporting_period=self.period, prepared_by=self.author)

    def make_user(self, username, code, **location):
        user = User.objects.create_user(username=username)
        role, _ = Role.objects.get_or_create(code=code, defaults={"name":Role(code=code).get_code_display()})
        UserRoleAssignment.objects.create(user=user, role=role)
        UserLocationAssignment.objects.create(user=user, **location)
        return user

    def complete_report(self):
        self.report.section_statuses.update(status=ReportSectionStatus.Status.COMPLETE, completion_percentage=100)
        FinalDeclaration.objects.create(report=self.report, declared_by=self.author, declaration_text="Accurate", acknowledged=True)

    def test_critical_quality_issue_blocks_submission(self):
        issues = validate_report(self.report)
        self.assertTrue(issues.filter(severity="critical").exists())
        with self.assertRaises(ValidationError):
            transition_report(report=self.report, user=self.author, action="mark_ready")

    def test_submission_error_is_human_readable_and_actionable(self):
        FinalDeclaration.objects.create(report=self.report, declared_by=self.author, declaration_text="Accurate", acknowledged=True)
        self.client.force_login(self.author)
        response = self.client.post(reverse("reporting:workflow_action", args=(self.report.uuid, "mark_ready")), follow=True)
        self.assertContains(response, "This report cannot be marked ready yet.")
        self.assertContains(response, "17 sections are not complete.")
        self.assertContains(response, "complete or confirm them unchanged")
        self.assertNotContains(response, "['This report")

    def test_complete_review_approval_and_lock_workflow(self):
        self.complete_report()
        transition_report(report=self.report, user=self.author, action="mark_ready")
        transition_report(report=self.report, user=self.author, action="submit")
        transition_report(report=self.report, user=self.reviewer, action="start_tikina_review")
        transition_report(report=self.report, user=self.reviewer, action="forward")
        transition_report(report=self.report, user=self.approver, action="approve", acknowledged=True)
        transition_report(report=self.report, user=self.approver, action="lock", acknowledged=True)
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, TNKReport.Status.LOCKED)
        self.assertEqual(self.report.approval_actions.count(), 6)
        self.assertEqual(IndicatorValue.objects.filter(village=self.village, reporting_period=self.period).count(), 91)

    def test_approval_actions_are_immutable(self):
        self.complete_report()
        action = transition_report(report=self.report, user=self.author, action="mark_ready")
        action.comment = "changed"
        with self.assertRaises(ValidationError):
            action.save()

    def test_exports_are_scoped_audited_and_exclude_personal_fields(self):
        self.client.force_login(self.author)
        for fmt, content_type in (("csv", "text/csv"), ("xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"), ("pdf", "application/pdf")):
            response = self.client.get(reverse("analytics:export", args=(fmt,)))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["Content-Type"], content_type)
        self.assertEqual(DataExportAudit.objects.count(), 3)
        csv_body = self.client.get(reverse("analytics:export", args=("csv",))).content.decode()
        self.assertNotIn("household_head_name", csv_body)
        xlsx_body = self.client.get(reverse("analytics:export", args=("xlsx",))).content
        with zipfile.ZipFile(io.BytesIO(xlsx_body)) as workbook:
            self.assertIn("xl/worksheets/sheet1.xml", workbook.namelist())

    def test_spreadsheet_formula_values_are_neutralised(self):
        self.assertEqual(safe_spreadsheet_value("=HYPERLINK('bad')"), "'=HYPERLINK('bad')")
        self.assertEqual(safe_spreadsheet_value("Tubou"), "Tubou")

    def test_scoped_dashboard_renders_charts_and_map(self):
        self.client.force_login(self.author)
        response = self.client.get(reverse("analytics:dashboard"), {"year": 2026, "quarter": 1})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "status-chart")
        self.assertContains(response, "village-map")

    def test_protected_document_requires_location_access(self):
        with override_settings(MEDIA_ROOT=settings.BASE_DIR / "test_media"):
            document = EvidenceDocument.objects.create(title="Evidence", document_type="report", file=SimpleUploadedFile("evidence.pdf", b"%PDF-1.4 test", content_type="application/pdf"), original_filename="evidence.pdf", file_size=13, mime_type="application/pdf", checksum="0" * 64, uploaded_by=self.author)
            EvidenceLink.objects.create(document=document, content_type=ContentType.objects.get_for_model(TNKReport), object_id=self.report.pk)
            validate_report(self.report)
            self.report.refresh_from_db()
            self.assertEqual(self.report.evidence_score, 100)
            self.client.force_login(self.author)
            self.assertEqual(self.client.get(reverse("documents:download", args=(document.uuid,))).status_code, 200)
            outsider = User.objects.create_user(username="outsider")
            self.client.force_login(outsider)
            self.assertEqual(self.client.get(reverse("documents:download", args=(document.uuid,))).status_code, 403)
