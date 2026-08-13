import hashlib
import json
import os
from datetime import date

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import BaseCommand, CommandError, call_command
from django.db import connection, transaction
from django.test import Client
from django.urls import reverse

from apps.accounts.models import Role, User, UserLocationAssignment, UserRoleAssignment
from apps.analytics.exports import csv_export, pdf_export, xlsx_export
from apps.analytics.models import DataExportAudit, IndicatorValue
from apps.core.security import can_view_document
from apps.documents.models import EvidenceDocument, EvidenceLink
from apps.locations.models import Province, Tikina, Village
from apps.reporting.models import ReportSectionStatus, ReportingPeriod, TNKReport
from apps.reporting.services import create_report
from apps.workflow.models import FinalDeclaration
from apps.workflow.services import transition_report


class Command(BaseCommand):
    help = "Run a fictional end-to-end rehearsal on an explicitly isolated PostgreSQL database."

    def add_arguments(self, parser):
        parser.add_argument("--verify-only", action="store_true")

    def _guard(self):
        name = str(connection.settings_dict.get("NAME", "")).lower()
        if connection.vendor != "postgresql":
            raise CommandError("The staging rehearsal requires PostgreSQL.")
        if os.getenv("TNK_ALLOW_STAGING_REHEARSAL", "").lower() != "true":
            raise CommandError("Set TNK_ALLOW_STAGING_REHEARSAL=true for an isolated rehearsal database.")
        if not any(marker in name for marker in ("stage", "staging", "rehearsal", "test")):
            raise CommandError("The database name must clearly identify staging, rehearsal, or test use.")

    def _summary(self):
        report = TNKReport.objects.filter(village__code="PH-A1", reporting_period__year=2099).first()
        document = EvidenceDocument.objects.filter(title="Phase H fictional evidence").first()
        evidence_ok = False
        if document:
            with document.file.open("rb") as handle:
                evidence_ok = hashlib.sha256(handle.read()).hexdigest() == document.checksum
        return {
            "database_vendor": connection.vendor,
            "report_count": TNKReport.objects.count(),
            "approved_report_found": bool(report and report.status == TNKReport.Status.APPROVED),
            "user_count": User.objects.count(),
            "role_count": Role.objects.count(),
            "indicator_value_count": IndicatorValue.objects.count(),
            "export_audit_count": DataExportAudit.objects.count(),
            "evidence_checksum_verified": evidence_ok,
        }

    @transaction.atomic
    def _run(self):
        if TNKReport.objects.exists():
            raise CommandError("The isolated rehearsal database must contain no TNK reports.")
        call_command("seed_reference_data", verbosity=0)

        province = Province.objects.create(code="PH", name_en="Phase H Test Province")
        tikina = Tikina.objects.create(province=province, code="PH-A", name_en="Phase H Tikina")
        village = Village.objects.create(tikina=tikina, code="PH-A1", name_en="Phase H Village")

        def create_user(username, role_code, **location):
            user = User.objects.create_user(username=username, password=None)
            UserRoleAssignment.objects.create(user=user, role=Role.objects.get(code=role_code))
            UserLocationAssignment.objects.create(user=user, **location)
            return user

        system = create_user("phase-h-system", Role.Codes.SYSTEM_ADMIN, province=province)
        author = create_user("phase-h-tnk", Role.Codes.TURAGA_NI_KORO, village=village)
        reviewer = create_user("phase-h-mata", Role.Codes.MATA_NI_TIKINA, tikina=tikina)
        approver = create_user("phase-h-roko", Role.Codes.ROKO_TUI, province=province)

        period = ReportingPeriod.objects.create(
            year=2099,
            quarter=1,
            start_date=date(2099, 1, 1),
            end_date=date(2099, 3, 31),
            submission_due_date=date(2099, 4, 30),
            is_open=True,
        )
        report = create_report(village=village, reporting_period=period, prepared_by=author)
        report.section_statuses.update(status=ReportSectionStatus.Status.COMPLETE, completion_percentage=100)
        FinalDeclaration.objects.create(
            report=report,
            declared_by=author,
            declaration_text="Fictional staging rehearsal declaration.",
            acknowledged=True,
        )

        upload = SimpleUploadedFile(
            "phase-h-evidence.pdf",
            b"%PDF-1.4\n% Fictional Phase H staging evidence\n%%EOF\n",
            content_type="application/pdf",
        )
        document = EvidenceDocument(
            title="Phase H fictional evidence",
            document_type="staging_rehearsal",
            file=upload,
            original_filename=upload.name,
            file_size=upload.size,
            mime_type="application/pdf",
            checksum="0" * 64,
            description="Synthetic evidence used only for staging restore verification.",
            confidentiality_level="restricted",
            uploaded_by=author,
        )
        document.full_clean()
        document.save()
        EvidenceLink.objects.create(
            document=document,
            content_type=ContentType.objects.get_for_model(report),
            object_id=report.pk,
        )

        transition_report(report=report, user=author, action="mark_ready")
        transition_report(report=report, user=author, action="submit")
        transition_report(report=report, user=reviewer, action="start_tikina_review")
        transition_report(report=report, user=reviewer, action="forward")
        transition_report(report=report, user=approver, action="approve", acknowledged=True)
        report.refresh_from_db()
        if report.status != TNKReport.Status.APPROVED:
            raise CommandError("The rehearsal report did not reach approved status.")
        if not can_view_document(approver, document):
            raise CommandError("The authorised reviewer could not access protected evidence.")
        rehearsal_host = next(
            (host for host in settings.ALLOWED_HOSTS if host and host != "*" and not host.startswith(".")),
            "localhost",
        )
        client = Client(HTTP_HOST=rehearsal_host)
        client.force_login(approver)
        download = client.get(reverse("documents:download", args=(document.uuid,)), secure=True)
        downloaded_bytes = b"".join(download.streaming_content) if download.status_code == 200 else b""
        if hashlib.sha256(downloaded_bytes).hexdigest() != document.checksum:
            raise CommandError("Protected evidence download or checksum verification failed.")

        reports = TNKReport.objects.filter(pk=report.pk)
        responses = (
            csv_export(system, reports, {"rehearsal": "phase_h"}, "Phase H staging rehearsal"),
            xlsx_export(system, reports, {"rehearsal": "phase_h"}, "Phase H staging rehearsal"),
            pdf_export(system, reports, {"rehearsal": "phase_h"}, "Phase H staging rehearsal"),
        )
        if not all(response.content for response in responses):
            raise CommandError("One or more rehearsal exports were empty.")

    def handle(self, *args, **options):
        self._guard()
        if not options["verify_only"]:
            self._run()
        result = self._summary()
        required = (result["approved_report_found"], result["evidence_checksum_verified"])
        if not all(required):
            raise CommandError(f"Rehearsal verification failed: {json.dumps(result, sort_keys=True)}")
        self.stdout.write(f"PHASE_H_RESULT={json.dumps(result, sort_keys=True)}")
        self.stdout.write(self.style.SUCCESS("Phase H fictional staging rehearsal passed."))
