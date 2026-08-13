from datetime import date

from django.contrib import admin
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import RequestFactory, TestCase
from django.urls import reverse

from apps.accounts.models import Role, User, UserLocationAssignment, UserRoleAssignment
from apps.culture.models import TraditionalTitle, TraditionalTitleAppointment, TraditionalUnit
from apps.culture.services import replace_traditional_title_appointment
from apps.economy.models import VillageBusiness
from apps.economy.services import record_business_change
from apps.governance.models import CommitteeMember, OfficialAppointment, OfficialRole, PersonReference, VillageCommittee
from apps.governance.services import replace_committee, replace_committee_member, replace_official_appointment
from apps.infrastructure.models import AssetMovement, VillageAsset, VillageEnergyAsset, VillageWaterSource
from apps.infrastructure.services import replace_energy_asset, replace_village_asset, replace_water_source
from apps.locations.models import Province, Tikina, Village
from apps.population.models import Household
from apps.population.services import replace_household
from apps.projects.models import IVDPProject
from apps.projects.services import update_project_master
from apps.reporting.models import ReportMasterSnapshot, ReportSectionStatus, ReportingPeriod
from apps.reporting.section_entries import entry_rows
from apps.reporting.section_registry import get_entry_config
from apps.reporting.services import create_report
from apps.workflow.models import FinalDeclaration
from apps.workflow.services import transition_report


class HistoricalMasterDataTests(TestCase):
    def setUp(self):
        self.province = Province.objects.create(code="HIST", name_en="Historical Province")
        self.tikina = Tikina.objects.create(province=self.province, code="HT", name_en="Historical Tikina")
        self.village = Village.objects.create(tikina=self.tikina, code="HV", name_en="Historical Village")
        self.user = User.objects.create_user(username="historical-author")
        role = Role.objects.create(code=Role.Codes.TURAGA_NI_KORO, name="Turaga ni Koro")
        UserRoleAssignment.objects.create(user=self.user, role=role)
        UserLocationAssignment.objects.create(user=self.user, village=self.village)
        self.q1 = ReportingPeriod.objects.create(year=2026, quarter=1, start_date=date(2026, 1, 1), end_date=date(2026, 3, 31), submission_due_date=date(2026, 12, 1), is_open=True)
        self.report = create_report(village=self.village, reporting_period=self.q1, prepared_by=self.user)
        self.official_role = OfficialRole.objects.create(code="TNK", name_en="Turaga ni Koro")
        self.person_a = PersonReference.objects.create(full_name="Official A", home_village=self.village)
        self.appointment = OfficialAppointment.objects.create(
            person=self.person_a,
            village=self.village,
            role=self.official_role,
            appointment_date=date(2026, 1, 1),
            effective_from=date(2026, 1, 1),
            confirmation_status="confirmed",
            change_reason="Initial appointment",
        )
        self.committee = VillageCommittee.objects.create(
            village=self.village,
            committee_type="development",
            name="Q1 Development Committee",
            formed_date=date(2026, 1, 1),
        )
        self.business = VillageBusiness.objects.create(
            village=self.village,
            business_name="Q1 Shop",
            business_sector="retail",
            owner_type="individual",
            owner_name="Owner A",
            start_date=date(2025, 1, 1),
            operating_status="active",
        )
        self.project = IVDPProject.objects.create(
            project_code="P1",
            village=self.village,
            project_name="Q1 Water Project",
            project_category="water",
            problem_being_addressed="Water access",
            priority="high",
            planned_start_date=date(2026, 1, 10),
            project_status="active",
        )
        self.household = Household.objects.create(
            household_code="H1",
            village=self.village,
            household_head_name="Household A",
            household_size=4,
            effective_from=date(2026, 1, 1),
        )

    def complete_and_mark_ready(self):
        self.report.section_statuses.update(status=ReportSectionStatus.Status.COMPLETE, completion_percentage=100)
        FinalDeclaration.objects.update_or_create(
            report=self.report,
            defaults={"declared_by": self.user, "declaration_text": "Accurate", "acknowledged": True},
        )
        transition_report(report=self.report, user=self.user, action="mark_ready")
        self.report.refresh_from_db()

    def summaries(self, report, section_code, entry_key):
        config = get_entry_config(section_code, entry_key)
        return [row["summary"] for row in entry_rows(config, report)]

    def test_q1_snapshot_remains_unchanged_after_q3_master_changes(self):
        self.complete_and_mark_ready()
        self.assertIsNotNone(self.report.master_snapshot_captured_at)
        self.assertIn("Official A", " ".join(self.summaries(self.report, "leadership_governance", "appointment")))

        person_b = PersonReference.objects.create(full_name="Official B", home_village=self.village)
        replace_official_appointment(
            current=self.appointment,
            user=self.user,
            person=person_b,
            appointment_date=date(2026, 7, 1),
            effective_from=date(2026, 7, 1),
            confirmation_status="confirmed",
            appointment_reference="Q3 appointment",
            change_reason="New office holder",
        )
        replace_committee(
            current=self.committee,
            user=self.user,
            formed_date=date(2026, 7, 1),
            reason="New committee elected",
            name="Q3 Development Committee",
        )
        record_business_change(
            business=self.business,
            user=self.user,
            effective_date=date(2026, 7, 1),
            reason="Ownership transfer",
            business_name="Q3 Shop",
            owner_name="Owner B",
        )
        update_project_master(
            project=self.project,
            user=self.user,
            effective_date=date(2026, 7, 1),
            reason="Approved project rename",
            project_name="Q3 Water Project",
        )

        self.assertEqual(self.summaries(self.report, "leadership_governance", "appointment"), ["Official A — Turaga ni Koro"])
        self.assertEqual(self.summaries(self.report, "leadership_governance", "committee"), ["Q1 Development Committee"])
        self.assertEqual(self.summaries(self.report, "business_finance", "business"), ["Q1 Shop"])
        self.assertEqual(self.summaries(self.report, "ivdp_projects", "project"), ["Q1 Water Project"])

        self.client.force_login(self.user)
        response = self.client.get(reverse("reporting:section_update", args=(self.report.uuid, "leadership_governance")))
        self.assertContains(response, "Official A")
        self.assertNotContains(response, "Official B")

    def test_effective_dated_replacements_close_old_rows(self):
        person_b = PersonReference.objects.create(full_name="Official B", home_village=self.village)
        replacement = replace_official_appointment(
            current=self.appointment,
            user=self.user,
            person=person_b,
            appointment_date=date(2026, 7, 1),
            effective_from=date(2026, 7, 1),
            confirmation_status="confirmed",
            change_reason="New office holder",
        )
        self.appointment.refresh_from_db()
        self.assertFalse(self.appointment.is_current)
        self.assertEqual(self.appointment.effective_to, date(2026, 6, 30))
        self.assertTrue(replacement.is_current)
        self.assertIsNone(replacement.effective_to)

        household_v2 = replace_household(
            current=self.household,
            user=self.user,
            effective_from=date(2026, 7, 1),
            household_size=5,
        )
        self.household.refresh_from_db()
        self.assertFalse(self.household.is_active)
        self.assertEqual(self.household.effective_to, date(2026, 6, 30))
        self.assertEqual(household_v2.household_size, 5)

        member = CommitteeMember.objects.create(
            committee=self.committee,
            person=self.person_a,
            position="Chair",
            joined_date=date(2026, 1, 1),
        )
        member_v2 = replace_committee_member(
            current=member,
            user=self.user,
            person=person_b,
            joined_date=date(2026, 7, 1),
            position="Chair",
        )
        member.refresh_from_db()
        self.assertEqual(member.left_date, date(2026, 6, 30))
        self.assertFalse(member.is_active)
        self.assertEqual(member_v2.person, person_b)

        unit = TraditionalUnit.objects.create(village=self.village, unit_type="yavusa", name="Yavusa A")
        title = TraditionalTitle.objects.create(traditional_unit=unit, title_type="chief", title_name="Tui A", status="filled", confirmation_stage="confirmed", confirmation_date=date(2026, 1, 1))
        title_appointment = TraditionalTitleAppointment.objects.create(title=title, person=self.person_a, effective_from=date(2026, 1, 1))
        title_v2 = replace_traditional_title_appointment(current=title_appointment, user=self.user, person=person_b, effective_from=date(2026, 7, 1))
        title_appointment.refresh_from_db()
        self.assertEqual(title_appointment.effective_to, date(2026, 6, 30))
        self.assertFalse(title_appointment.is_current)
        self.assertEqual(title_v2.person, person_b)

    def test_invalid_same_date_replacement_is_rejected_without_mutation(self):
        with self.assertRaises(ValidationError):
            replace_household(current=self.household, user=self.user, effective_from=date(2026, 1, 1), household_size=9)
        self.household.refresh_from_db()
        self.assertTrue(self.household.is_active)
        self.assertIsNone(self.household.effective_to)
        self.assertEqual(Household.objects.filter(household_code="H1").count(), 1)

    def test_master_replacement_requires_role_and_village_assignment(self):
        outsider = User.objects.create_user(username="historical-outsider")
        with self.assertRaises(PermissionDenied):
            replace_household(
                current=self.household,
                user=outsider,
                effective_from=date(2026, 7, 1),
                household_size=9,
            )
        self.household.refresh_from_db()
        self.assertTrue(self.household.is_active)
        self.assertIsNone(self.household.effective_to)

    def test_infrastructure_replacements_preserve_inactive_predecessors(self):
        asset = VillageAsset.objects.create(village=self.village, asset_code="A1", asset_type="generator", asset_name="Old generator", quantity=1, condition="poor", operational_status="working")
        source = VillageWaterSource.objects.create(village=self.village, source_type="borehole", source_name="Old borehole", operational_status="working", availability_status="reliable", water_quality_status="safe", condition="fair", primary_or_backup="primary")
        energy = VillageEnergyAsset.objects.create(village=self.village, asset_type="solar", condition="poor", operational_status="working", fuel_or_energy_type="solar")
        new_asset = replace_village_asset(current=asset, user=self.user, effective_date=date(2026, 7, 1), reason="Asset replaced", asset_code="A2", asset_name="New generator", condition="good")
        new_source = replace_water_source(current=source, user=self.user, effective_date=date(2026, 7, 1), reason="Source replaced", source_name="New borehole", condition="good")
        new_energy = replace_energy_asset(current=energy, user=self.user, effective_date=date(2026, 7, 1), reason="Energy asset replaced", condition="good")
        asset.refresh_from_db(); source.refresh_from_db(); energy.refresh_from_db()
        self.assertFalse(asset.is_active)
        self.assertFalse(source.is_active)
        self.assertFalse(energy.is_active)
        self.assertTrue(new_asset.is_active and new_source.is_active and new_energy.is_active)
        self.assertTrue(AssetMovement.objects.filter(asset=asset, movement_type="replacement").exists())

    def test_frozen_snapshots_are_immutable_and_reopen_recaptures(self):
        self.complete_and_mark_ready()
        snapshot = ReportMasterSnapshot.objects.filter(report=self.report, entry_key="project").get()
        snapshot.summary = "Tampered"
        with self.assertRaises(ValidationError):
            snapshot.save(update_fields=("summary",))
        with self.assertRaises(ValidationError):
            ReportMasterSnapshot.objects.filter(report=self.report).delete()
        with self.assertRaises(ValidationError):
            ReportMasterSnapshot.objects.filter(report=self.report).update(summary="Tampered")
        with self.assertRaises(ValidationError):
            ReportMasterSnapshot.objects.create(
                report=self.report,
                section_code="ivdp_projects",
                entry_key="project",
                source_model="projects.IVDPProject",
                source_identifier="invented",
                summary="Invented",
            )

        transition_report(report=self.report, user=self.user, action="reopen_draft")
        update_project_master(project=self.project, user=self.user, effective_date=date(2026, 3, 1), reason="Correction before submission", project_name="Corrected Q1 Project")
        self.complete_and_mark_ready()
        self.assertEqual(self.summaries(self.report, "ivdp_projects", "project"), ["Corrected Q1 Project"])

    def test_historical_master_admin_is_read_only_and_non_deletable(self):
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save(update_fields=("is_staff", "is_superuser"))
        request = RequestFactory().get("/admin/")
        request.user = self.user
        for instance in (self.appointment, self.committee, self.business, self.project, self.household):
            with self.subTest(model=instance._meta.label):
                model_admin = admin.site._registry[type(instance)]
                readonly = model_admin.get_readonly_fields(request, instance)
                self.assertEqual(set(readonly), {field.name for field in instance._meta.concrete_fields})
                self.assertFalse(model_admin.has_delete_permission(request, instance))
                self.assertNotIn("delete_selected", model_admin.get_actions(request))
