from datetime import date
from decimal import Decimal
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import Role, User, UserLocationAssignment, UserRoleAssignment
from apps.analytics.exports import pdf_export, xlsx_export
from apps.analytics.models import DataExportAudit, IndicatorValue
from apps.audit.models import AuditEvent
from apps.documents.models import EvidenceDocument
from apps.governance.models import CommitteeMeeting, PersonReference, VillageCommittee
from apps.infrastructure.models import SanitationSnapshot, VillageWaterSource
from apps.locations.models import Province, Tikina, Village
from apps.population.models import AgeGroup, Household, PopulationMovement, PopulationSnapshot
from apps.projects.models import IVDPProject, IVDPProjectProgress
from apps.reporting.models import ReportSectionStatus, ReportingPeriod, TNKReport
from apps.reporting.services import create_report
from apps.wellbeing.models import HealthCondition, HealthConditionSnapshot
from apps.workflow.models import FinalDeclaration


@override_settings(MEDIA_ROOT=Path(__file__).resolve().parents[1] / "test_media")
class FinalEndToEndAcceptanceTests(TestCase):
    def setUp(self):
        call_command("seed_reference_data", verbosity=0)
        self.province = Province.objects.create(code="ACCEPT", name_en="Test Province")
        self.tikina_a = Tikina.objects.create(province=self.province, code="A", name_en="Tikina A")
        self.tikina_b = Tikina.objects.create(province=self.province, code="B", name_en="Tikina B")
        self.village_a1 = Village.objects.create(tikina=self.tikina_a, code="A1", name_en="Village A1")
        self.village_a2 = Village.objects.create(tikina=self.tikina_a, code="A2", name_en="Village A2")
        self.village_b1 = Village.objects.create(tikina=self.tikina_b, code="B1", name_en="Village B1")
        self.users = {
            "system": self.make_user("accept-system", Role.Codes.SYSTEM_ADMIN, province=self.province),
            "provincial": self.make_user("accept-provincial", Role.Codes.PROVINCIAL_ADMIN, province=self.province),
            "roko_tui": self.make_user("accept-roko-tui", Role.Codes.ROKO_TUI, province=self.province),
            "roko_veivuke": self.make_user("accept-roko-veivuke", Role.Codes.ROKO_VEIVUKE, tikina=self.tikina_a),
            "mata_a": self.make_user("accept-mata-a", Role.Codes.MATA_NI_TIKINA, tikina=self.tikina_a),
            "mata_b": self.make_user("accept-mata-b", Role.Codes.MATA_NI_TIKINA, tikina=self.tikina_b),
            "tnk_a1": self.make_user("accept-tnk-a1", Role.Codes.TURAGA_NI_KORO, village=self.village_a1),
            "tnk_a2": self.make_user("accept-tnk-a2", Role.Codes.TURAGA_NI_KORO, village=self.village_a2),
            "assistant": self.make_user("accept-assistant", Role.Codes.VILLAGE_DATA_ASSISTANT, village=self.village_a1),
            "nurse": self.make_user("accept-nurse", Role.Codes.VILLAGE_NURSE, village=self.village_a1),
            "analyst": self.make_user("accept-analyst", Role.Codes.READ_ONLY_ANALYST, province=self.province),
            "auditor": self.make_user("accept-auditor", Role.Codes.AUDITOR, province=self.province),
        }
        self.previous_period = ReportingPeriod.objects.create(
            year=2025,
            quarter=4,
            start_date=date(2025, 10, 1),
            end_date=date(2025, 12, 31),
            submission_due_date=date(2026, 1, 31),
            is_open=True,
        )
        self.period = ReportingPeriod.objects.create(
            year=2026,
            quarter=3,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 9, 30),
            submission_due_date=date(2026, 12, 31),
            is_open=True,
        )

    def make_user(self, username, role_code, **location):
        user = User.objects.create_user(username=username, password="Acceptance-only-password-42", is_staff=True)
        UserRoleAssignment.objects.create(user=user, role=Role.objects.get(code=role_code))
        UserLocationAssignment.objects.create(user=user, **location)
        return user

    def analytical_fields(self, unit="count"):
        return {
            "measurement_date": date(2026, 8, 1),
            "measurement_unit": unit,
            "data_source": "village_register",
            "collection_method": "Verified register count",
            "source_reference": "Fictional acceptance register",
            "verification_status": "verified",
            "verified_by": self.users["provincial"],
            "confidence_level": "high",
            "created_by": self.users["tnk_a1"],
        }

    def post_action(self, actor, report, action, data=None):
        self.client.force_login(self.users[actor])
        response = self.client.post(
            reverse("reporting:workflow_action", args=(report.uuid, action)),
            data or {},
        )
        self.assertEqual(response.status_code, 302)
        report.refresh_from_db()

    def test_complete_multi_role_multi_location_acceptance_scenario(self):
        previous = create_report(
            village=self.village_a1,
            reporting_period=self.previous_period,
            prepared_by=self.users["tnk_a1"],
        )
        TNKReport.objects.filter(pk=previous.pk).update(status=TNKReport.Status.APPROVED)
        report = create_report(
            village=self.village_a1,
            reporting_period=self.period,
            prepared_by=self.users["tnk_a1"],
        )
        self.assertEqual(report.previous_report, previous)
        self.assertEqual(report.section_statuses.count(), 17)

        self.client.force_login(self.users["tnk_a1"])
        detail = self.client.get(reverse("reporting:detail", args=(report.uuid,)))
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "2025 Q4")

        age_group = AgeGroup.objects.get(code="25_34")
        person = PersonReference.objects.create(full_name="Fictional Committee Chair", home_village=self.village_a1)
        committee = VillageCommittee.objects.create(
            village=self.village_a1,
            committee_type="development",
            name="Village A1 Development Committee",
            formed_date=date(2024, 1, 1),
            chairperson=person,
            annual_plan_available=True,
        )
        CommitteeMeeting.objects.create(
            committee=committee,
            report=report,
            meeting_date=date(2026, 7, 15),
            chaired_by=person,
            total_attendance=12,
            male_attendance=7,
            female_attendance=5,
            youth_attendance=3,
            disability_attendance=1,
            quorum_achieved=True,
            minutes_available=True,
        )
        household = Household.objects.create(
            household_code="A1-HH-001",
            village=self.village_a1,
            household_head_name="Fictional Household",
            household_size=5,
            male_count=2,
            female_count=3,
            child_count=2,
            elderly_count=1,
            effective_from=date(2026, 7, 1),
            verification_status="verified",
        )
        movement = PopulationMovement.objects.create(
            village=self.village_a1,
            reporting_period=self.period,
            movement_type="birth",
            movement_date=date(2026, 7, 20),
            gender="female",
            age_group=age_group,
            count=1,
            data_source="village_register",
            verified=True,
        )
        population = PopulationSnapshot.objects.create(
            report=report,
            village=self.village_a1,
            age_group=age_group,
            gender="female",
            resident_status="permanent_resident",
            count=100,
            **self.analytical_fields(),
        )
        water = VillageWaterSource.objects.create(
            village=self.village_a1,
            source_type="piped",
            source_name="Fictional Main Supply",
            operational_status="operational",
            capacity_litres=Decimal("10000"),
            households_served=1,
            people_served=5,
            availability_status="reliable",
            average_days_unavailable_per_month=Decimal("0"),
            water_quality_status="safe",
            condition="good",
            primary_or_backup="primary",
        )
        SanitationSnapshot.objects.create(
            report=report,
            toilet_type="flush",
            functional_count=1,
            non_functional_count=0,
            private_count=1,
            safely_managed_count=1,
            flood_vulnerable_count=0,
            **self.analytical_fields(),
        )
        HealthConditionSnapshot.objects.create(
            report=report,
            health_condition=HealthCondition.objects.get(code="ari"),
            age_group=age_group,
            gender="female",
            new_cases=2,
            existing_cases=3,
            referred_cases=1,
            recovered_cases=2,
            deaths=0,
            **self.analytical_fields(),
        )
        project = IVDPProject.objects.create(
            project_code="A1-WATER-01",
            village=self.village_a1,
            project_name="Fictional water resilience project",
            project_category="water",
            problem_being_addressed="Dry-season supply interruption",
            measurement_unit="percent",
            priority="high",
            planned_start_date=date(2026, 7, 1),
            planned_end_date=date(2026, 12, 31),
            actual_start_date=date(2026, 7, 5),
            approved_budget=Decimal("25000"),
            actual_expenditure=Decimal("5000"),
            project_status="in_progress",
            physical_progress_percentage=Decimal("25"),
            financial_progress_percentage=Decimal("20"),
            expected_beneficiaries=100,
            male_beneficiaries=45,
            female_beneficiaries=50,
            youth_beneficiaries=30,
        )
        IVDPProjectProgress.objects.create(
            project=project,
            report=report,
            reporting_date=date(2026, 8, 1),
            work_completed="Tank foundation completed",
            progress_percentage=Decimal("25"),
            expenditure_to_date=Decimal("5000"),
            next_activity="Install tank",
            next_activity_due_date=date(2026, 9, 1),
            risk_level="medium",
        )
        self.assertEqual(movement.count, 1)
        self.assertEqual(household.household_size, 5)
        self.assertTrue(water.is_active)

        evidence_file = SimpleUploadedFile(
            "acceptance-evidence.pdf",
            b"%PDF-1.4\n% Fictional acceptance evidence\n%%EOF\n",
            content_type="application/pdf",
        )
        upload = self.client.post(
            reverse("reporting:evidence_upload", args=(report.uuid,)),
            {
                "title": "Fictional acceptance evidence",
                "document_type": "meeting_minutes",
                "description": "Synthetic acceptance evidence only.",
                "confidentiality_level": "restricted",
                "file": evidence_file,
            },
        )
        self.assertEqual(upload.status_code, 302)
        evidence = EvidenceDocument.objects.get(title="Fictional acceptance evidence")
        self.addCleanup(evidence.file.storage.delete, evidence.file.name)

        report.section_statuses.update(status=ReportSectionStatus.Status.COMPLETE, completion_percentage=100)
        FinalDeclaration.objects.create(
            report=report,
            declared_by=self.users["tnk_a1"],
            declaration_text="Complete and accurate fictional report.",
            acknowledged=True,
        )
        validation = self.client.post(reverse("reporting:validate", args=(report.uuid,)))
        self.assertEqual(validation.status_code, 302)
        report.refresh_from_db()
        self.assertIsNotNone(report.data_quality_score)

        self.post_action("tnk_a1", report, "mark_ready")
        self.assertGreaterEqual(report.master_snapshots.count(), 5)
        self.post_action("tnk_a1", report, "submit")
        self.post_action("mata_a", report, "start_tikina_review")
        self.post_action("mata_a", report, "return", {"comment": "Correct the verified population total."})
        self.assertEqual(report.status, TNKReport.Status.RETURNED_TO_VILLAGE)

        population.count = 101
        population.full_clean()
        population.save(update_fields=("count", "updated_at"))
        self.client.force_login(self.users["tnk_a1"])
        declaration = self.client.post(reverse("reporting:declare", args=(report.uuid,)), {"acknowledged": "on"})
        self.assertEqual(declaration.status_code, 302)
        self.post_action("tnk_a1", report, "mark_ready")
        self.post_action("tnk_a1", report, "submit")
        self.post_action("roko_veivuke", report, "start_tikina_review")
        self.post_action("roko_veivuke", report, "forward")
        self.post_action("roko_tui", report, "approve", {"acknowledged": "on"})
        self.post_action("system", report, "lock", {"acknowledged": "on"})
        self.assertEqual(report.status, TNKReport.Status.LOCKED)

        self.client.force_login(self.users["tnk_a1"])
        locked_edit = self.client.post(
            reverse(
                "reporting:entry_edit",
                args=(report.uuid, "population_households", "population", population.uuid),
            ),
            {"count": 999},
        )
        self.assertEqual(locked_edit.status_code, 403)

        values = IndicatorValue.objects.filter(reporting_period=self.period, village=self.village_a1)
        self.assertTrue(values.filter(indicator__code="total_population", value=Decimal("101")).exists())
        self.client.force_login(self.users["analyst"])
        dashboard = self.client.get(reverse("analytics:dashboard"))
        self.assertEqual(dashboard.status_code, 200)
        self.assertContains(dashboard, "Total population")

        reports = TNKReport.objects.filter(pk=report.pk)
        excel = xlsx_export(self.users["system"], reports, {"village": str(self.village_a1.pk)}, "Final acceptance")
        pdf = pdf_export(self.users["system"], reports, {"village": str(self.village_a1.pk)}, "Final acceptance")
        self.assertTrue(excel.content.startswith(b"PK"))
        self.assertTrue(pdf.content.startswith(b"%PDF"))
        self.assertEqual(DataExportAudit.objects.filter(export_reason="Final acceptance").count(), 2)

        self.client.force_login(self.users["auditor"])
        authorised_download = self.client.get(reverse("documents:download", args=(evidence.uuid,)))
        self.assertEqual(authorised_download.status_code, 200)
        self.assertTrue(b"".join(authorised_download.streaming_content).startswith(b"%PDF"))
        self.client.force_login(self.users["analyst"])
        self.assertEqual(self.client.get(reverse("documents:download", args=(evidence.uuid,))).status_code, 403)

        report_actions = AuditEvent.objects.filter(object_uuid=report.uuid, action__startswith="report.")
        self.assertGreaterEqual(report_actions.count(), 11)
        self.assertTrue(AuditEvent.objects.filter(object_uuid=evidence.uuid, action="document.accessed").exists())
        self.assertTrue(AuditEvent.objects.filter(action="export.created").exists())

        self.client.force_login(self.users["tnk_a2"])
        self.assertEqual(self.client.get(reverse("reporting:detail", args=(report.uuid,))).status_code, 403)
        self.assertEqual(self.client.get(reverse("documents:download", args=(evidence.uuid,))).status_code, 403)
        self.client.force_login(self.users["mata_b"])
        self.assertEqual(self.client.get(reverse("reporting:detail", args=(report.uuid,))).status_code, 403)
