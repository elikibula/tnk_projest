from datetime import date, datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import BaseCommand, CommandError, call_command
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Role, User, UserLocationAssignment, UserRoleAssignment
from apps.culture.models import CulturalKnowledgeRecord, TraditionalTitle, TraditionalUnit
from apps.data_quality.services import validate_report
from apps.documents.models import EvidenceDocument, EvidenceLink
from apps.economy.models import (
    CropProductionSnapshot,
    CropType,
    FoodSecuritySnapshot,
    VillageBusiness,
    VillageFinancialAccount,
    VillageFinancialSnapshot,
)
from apps.governance.models import (
    CommitteeMeeting,
    MeetingDecision,
    OfficialAppointment,
    OfficialRole,
    PersonReference,
    TrainingActivity,
    VillageCommittee,
    VillageVisit,
)
from apps.infrastructure.models import (
    EnergySnapshot,
    HousingSnapshot,
    SanitationSnapshot,
    VillageAsset,
    VillageEnergyAsset,
    VillageWaterSource,
    WasteCollectionActivity,
    WasteFacility,
    WaterInterruption,
    WaterMaintenanceActivity,
    WaterQualityTest,
)
from apps.locations.models import Province, Tikina, Village
from apps.population.models import AgeGroup, Household, PopulationMovement, PopulationSnapshot
from apps.projects.models import IVDPProject, IVDPProjectProgress, ProjectMilestone, ProjectRisk
from apps.reporting.models import ReportSectionStatus, ReportingPeriod, TNKReport
from apps.reporting.progress import recalculate_report_progress
from apps.reporting.services import create_report
from apps.resilience.models import (
    ClimateImpactObservation,
    DisasterIncident,
    EvacuationCentre,
    VillageDisasterPreparedness,
)
from apps.wellbeing.models import (
    CommunitySafetyIncident,
    DisabilitySnapshot,
    DisabilityType,
    HealthCondition,
    HealthConditionSnapshot,
    OffenceType,
    VillageHealthAccessSnapshot,
)
from apps.workflow.models import FinalDeclaration
from apps.workflow.services import transition_report


DEMO_PASSWORD = "Demo-TNK-2026!"
DEMO_YEAR = 2099


class Command(BaseCommand):
    help = "Seed a complete, fictional, development-only TNK showcase dataset."

    def add_arguments(self, parser):
        parser.add_argument(
            "--show-credentials",
            action="store_true",
            help="Print all fictional role account usernames after seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Demo data can only be seeded while DEBUG=True. Never seed it in production.")

        call_command("seed_reference_data", verbosity=0)
        locations = self._locations()
        users = self._users(locations)

        if TNKReport.objects.filter(village__tikina__province=locations["province"], reporting_period__year=DEMO_YEAR).exists():
            self.stdout.write(self.style.WARNING("The complete fictional demo dataset is already installed; no records were duplicated."))
            self._print_credentials(users, options["show_credentials"])
            return

        periods = self._periods()
        previous = create_report(
            village=locations["a1"], reporting_period=periods["q1"], prepared_by=users["tnk_a1"]
        )
        current = create_report(
            village=locations["a1"], reporting_period=periods["q2"], prepared_by=users["tnk_a1"]
        )
        submitted = create_report(
            village=locations["a2"], reporting_period=periods["q2"], prepared_by=users["tnk_a2"]
        )
        reviewing = create_report(
            village=locations["b1"], reporting_period=periods["q2"], prepared_by=users["tnk_b1"]
        )

        self._all_entries(previous, users, offset=0)
        self._all_entries(current, users, offset=8)
        self._evidence(previous, users["tnk_a1"])
        self._evidence(current, users["tnk_a1"])
        self._complete(previous, users["tnk_a1"])
        self._complete(submitted, users["tnk_a2"])
        self._complete(reviewing, users["tnk_b1"])

        transition_report(report=previous, user=users["tnk_a1"], action="mark_ready")
        transition_report(report=previous, user=users["tnk_a1"], action="submit")
        transition_report(report=previous, user=users["mata_a"], action="start_tikina_review")
        transition_report(report=previous, user=users["mata_a"], action="forward")
        transition_report(report=previous, user=users["roko"], action="approve", acknowledged=True)

        transition_report(report=submitted, user=users["tnk_a2"], action="mark_ready")
        transition_report(report=submitted, user=users["tnk_a2"], action="submit")

        transition_report(report=reviewing, user=users["tnk_b1"], action="mark_ready")
        transition_report(report=reviewing, user=users["tnk_b1"], action="submit")
        transition_report(report=reviewing, user=users["mata_b"], action="start_tikina_review")

        validate_report(current)
        recalculate_report_progress(current)
        periods["q1"].is_open = False
        periods["q1"].is_locked = True
        periods["q1"].save(update_fields=("is_open", "is_locked", "updated_at"))

        self.stdout.write(
            self.style.SUCCESS(
                "Complete fictional demo seeded: 3 villages, 14 role accounts, 4 reports, all 42 entry types, workflow history, indicators, and evidence."
            )
        )
        self._print_credentials(users, True)

    def _locations(self):
        province, _ = Province.objects.update_or_create(
            code="DEMO", defaults={"name_en": "Fictional Test Province", "name_fj": "Yasana ni Vakatovolei"}
        )
        tikina_a, _ = Tikina.objects.update_or_create(
            province=province,
            code="DEMO-A",
            defaults={"name_en": "Fictional Coastal Tikina", "name_fj": "Tikina ni Baravi Vakatovolei"},
        )
        tikina_b, _ = Tikina.objects.update_or_create(
            province=province,
            code="DEMO-B",
            defaults={"name_en": "Fictional Highlands Tikina", "name_fj": "Tikina ni Colo Vakatovolei"},
        )
        villages = {}
        for key, tikina, code, name_en, name_fj, latitude, longitude in (
            ("a1", tikina_a, "DEMO-A1", "Fictional Vunidemo", "Vunivakatovolei", "-18.141600", "178.441900"),
            ("a2", tikina_a, "DEMO-A2", "Fictional Navutest", "Navuvakatovolei", "-18.158000", "178.432000"),
            ("b1", tikina_b, "DEMO-B1", "Fictional Korotest", "Korovakatovolei", "-17.900000", "178.250000"),
        ):
            villages[key], _ = Village.objects.update_or_create(
                tikina=tikina,
                code=code,
                defaults={
                    "name_en": name_en,
                    "name_fj": name_fj,
                    "island_name": "Fictional Island",
                    "latitude": Decimal(latitude),
                    "longitude": Decimal(longitude),
                    "postal_address": "Demo address only - no real household",
                    "contact_phone": "+679 000 0000",
                    "contact_email": f"{code.lower()}@example.invalid",
                },
            )
        return {"province": province, "tikina_a": tikina_a, "tikina_b": tikina_b, **villages}

    def _users(self, locations):
        definitions = {
            "system": ("demo_admin", "Demo", "System Admin", Role.Codes.SYSTEM_ADMIN, "province", locations["province"], True, True),
            "provincial": ("demo_provincial", "Demo", "Provincial Admin", Role.Codes.PROVINCIAL_ADMIN, "province", locations["province"], True, False),
            "roko": ("demo_roko_tui", "Demo", "Roko Tui", Role.Codes.ROKO_TUI, "province", locations["province"], False, False),
            "veivuke": ("demo_roko_veivuke", "Demo", "Roko Veivuke", Role.Codes.ROKO_VEIVUKE, "province", locations["province"], False, False),
            "mata_a": ("demo_mata_a", "Demo", "Mata Coastal", Role.Codes.MATA_NI_TIKINA, "tikina", locations["tikina_a"], False, False),
            "mata_b": ("demo_mata_b", "Demo", "Mata Highlands", Role.Codes.MATA_NI_TIKINA, "tikina", locations["tikina_b"], False, False),
            "tnk_a1": ("demo_tnk_a1", "Demo", "TNK Vunidemo", Role.Codes.TURAGA_NI_KORO, "village", locations["a1"], False, False),
            "tnk_a2": ("demo_tnk_a2", "Demo", "TNK Navutest", Role.Codes.TURAGA_NI_KORO, "village", locations["a2"], False, False),
            "tnk_b1": ("demo_tnk_b1", "Demo", "TNK Korotest", Role.Codes.TURAGA_NI_KORO, "village", locations["b1"], False, False),
            "assistant": ("demo_assistant", "Demo", "Data Assistant", Role.Codes.VILLAGE_DATA_ASSISTANT, "village", locations["a1"], False, False),
            "nurse": ("demo_nurse", "Demo", "Village Nurse", Role.Codes.VILLAGE_NURSE, "village", locations["a1"], False, False),
            "project": ("demo_project", "Demo", "Project Officer", Role.Codes.PROJECT_OFFICER, "village", locations["a1"], False, False),
            "analyst": ("demo_analyst", "Demo", "Analyst", Role.Codes.READ_ONLY_ANALYST, "province", locations["province"], False, False),
            "auditor": ("demo_auditor", "Demo", "Auditor", Role.Codes.AUDITOR, "province", locations["province"], True, False),
        }
        users = {}
        for key, (username, first, last, role_code, level, location, staff, superuser) in definitions.items():
            user, _ = User.objects.get_or_create(username=username)
            user.first_name = first
            user.last_name = last
            user.email = f"{username}@example.invalid"
            user.is_active = True
            user.is_staff = staff
            user.is_superuser = superuser
            user.set_password(DEMO_PASSWORD)
            user.save()
            UserRoleAssignment.objects.update_or_create(
                user=user, role=Role.objects.get(code=role_code), defaults={"is_active": True}
            )
            UserLocationAssignment.objects.filter(user=user).delete()
            assignment = UserLocationAssignment(user=user, **{level: location})
            assignment.full_clean()
            assignment.save()
            users[key] = user
        return users

    def _periods(self):
        q1, _ = ReportingPeriod.objects.update_or_create(
            year=DEMO_YEAR,
            quarter=1,
            defaults={
                "start_date": date(DEMO_YEAR, 1, 1),
                "end_date": date(DEMO_YEAR, 3, 31),
                "submission_due_date": date(DEMO_YEAR, 4, 30),
                "is_open": True,
                "is_locked": False,
            },
        )
        q2, _ = ReportingPeriod.objects.update_or_create(
            year=DEMO_YEAR,
            quarter=2,
            defaults={
                "start_date": date(DEMO_YEAR, 4, 1),
                "end_date": date(DEMO_YEAR, 6, 30),
                "submission_due_date": date(DEMO_YEAR, 7, 31),
                "is_open": True,
                "is_locked": False,
            },
        )
        return {"q1": q1, "q2": q2}

    def _analytical(self, report, user, measurement_date, unit="count"):
        return {
            "measurement_date": measurement_date,
            "measurement_unit": unit,
            "data_source": "village_register",
            "collection_method": "Fictional household register review",
            "source_reference": f"DEMO-{report.reporting_period.year}-Q{report.reporting_period.quarter}",
            "verification_status": "verified",
            "verified_by": user,
            "verified_at": timezone.now(),
            "confidence_level": "high",
            "notes": "Fictional demonstration data only.",
            "created_by": user,
            "updated_by": user,
        }

    def _all_entries(self, report, users, offset):
        village = report.village
        period = report.reporting_period
        measured = date(period.year, period.quarter * 3, 15)
        start = period.start_date
        author = report.prepared_by
        adult = AgeGroup.objects.get(code="25_34")
        child = AgeGroup.objects.get(code="5_9")
        analytical = self._analytical(report, author, measured)

        person, _ = PersonReference.objects.get_or_create(
            home_village=village,
            full_name=f"Fictional Mere {village.code}",
            defaults={"gender": "female", "phone": "+679 000 1000", "confidentiality_level": "confidential"},
        )
        OfficialAppointment.objects.get_or_create(
            village=village,
            person=person,
            role=OfficialRole.objects.get(code="turaga_ni_koro"),
            effective_from=date(2098, 1, 1),
            defaults={
                "appointment_date": date(2097, 12, 15),
                "confirmation_status": "confirmed",
                "appointment_reference": f"DEMO-APPT-{village.code}",
                "is_current": True,
            },
        )
        committee, _ = VillageCommittee.objects.get_or_create(
            village=village,
            committee_type="development",
            defaults={
                "name": f"{village.name_en} Development Committee",
                "formed_date": date(2098, 1, 1),
                "mandate": "Coordinate fictional village development activities.",
                "chairperson": person,
                "secretary": person,
                "constitution_available": True,
                "annual_plan_available": True,
                "bank_account_available": True,
            },
        )
        meeting, _ = CommitteeMeeting.objects.get_or_create(
            committee=committee,
            report=report,
            defaults={
                "meeting_date": start + timedelta(days=20),
                "chaired_by": person,
                "total_attendance": 24 + offset,
                "male_attendance": 12 + offset // 2,
                "female_attendance": 12 + offset // 2,
                "youth_attendance": 7,
                "disability_attendance": 2,
                "quorum_achieved": True,
                "minutes_available": True,
            },
        )
        MeetingDecision.objects.get_or_create(
            meeting=meeting,
            decision="Install two additional communal water tanks.",
            defaults={
                "responsible_person": "Fictional Water Committee",
                "priority": "high",
                "due_date": period.end_date,
                "status": "in_progress",
                "completion_percentage": Decimal("40"),
            },
        )
        VillageVisit.objects.get_or_create(
            report=report,
            visit_type="Quarterly support visit",
            defaults={
                "village": village,
                "officer_name": "Fictional Provincial Officer",
                "organisation": "Demo Provincial Office",
                "visit_date": start + timedelta(days=25),
                "purpose": "Review quarterly reporting and project delivery.",
                "findings": "Records were organised and community participation was strong.",
                "recommendations": "Continue monthly data verification.",
                "follow_up_required": True,
                "follow_up_due_date": period.end_date,
                "follow_up_status": "scheduled",
            },
        )
        TrainingActivity.objects.get_or_create(
            report=report,
            title="Fictional disaster preparedness training",
            defaults={
                "village": village,
                "category": "resilience",
                "provider": "Demo Disaster Office",
                "start_date": start + timedelta(days=30),
                "end_date": start + timedelta(days=31),
                "delivery_method": "Workshop",
                "target_group": "Village households",
                "male_participants": 15,
                "female_participants": 17,
                "youth_participants": 10,
                "participants_with_disability": 2,
                "total_completed": 30,
                "cost": Decimal("1250"),
                "funding_source": "Fictional grant",
                "expected_outcome": "Improved evacuation readiness.",
                "actual_outcome": "A drill roster and contact tree were completed.",
            },
        )

        population_rows = ((adult, "female", 54 + offset), (adult, "male", 51 + offset), (child, "female", 31 + offset))
        for age_group, gender, count in population_rows:
            PopulationSnapshot.objects.get_or_create(
                report=report,
                village=village,
                age_group=age_group,
                gender=gender,
                resident_status="permanent_resident",
                defaults={"count": count, **analytical},
            )
        PopulationMovement.objects.get_or_create(
            village=village,
            reporting_period=period,
            movement_type="birth",
            movement_date=start + timedelta(days=40),
            defaults={"gender": "female", "age_group": child, "count": 2, "data_source": "village_register", "verified": True},
        )
        for number in range(1, 42):
            household_size = 4 + (number % 3)
            Household.objects.get_or_create(
                village=village,
                household_code=f"{village.code}-HH-{number:03}",
                effective_from=date(2098, 1, 1),
                defaults={
                    "household_head_name": f"Fictional Household {number}",
                    "household_size": household_size,
                    "male_count": 2,
                    "female_count": household_size - 2,
                    "child_count": 2 if household_size >= 5 else 1,
                    "elderly_count": 1 if number % 4 == 0 else 0,
                    "disability_count": 1 if number == 2 else 0,
                    "primary_livelihood": "Mixed farming and fishing",
                    "housing_type": "Timber and concrete",
                    "water_source": "Piped communal supply",
                    "toilet_type": "Flush/septic",
                    "energy_source": "Grid and solar",
                    "vulnerability_status": "requires_support" if number == 2 else "standard",
                    "verification_status": "verified",
                },
            )

        HousingSnapshot.objects.get_or_create(
            report=report,
            structure_type="permanent",
            construction_material="timber_and_concrete",
            occupancy_status="occupied",
            defaults={"condition": "good", "count": 38 + offset, **analytical},
        )
        VillageAsset.objects.get_or_create(
            village=village,
            asset_code=f"{village.code}-HALL",
            defaults={
                "asset_type": "community_hall",
                "asset_name": "Fictional Community Hall",
                "quantity": 1,
                "acquisition_date": date(2096, 5, 1),
                "acquisition_cost": Decimal("85000"),
                "estimated_current_value": Decimal("78000"),
                "funding_source": "Fictional development grant",
                "custodian": "Village Development Committee",
                "condition": "good",
                "operational_status": "operational",
            },
        )

        water, _ = VillageWaterSource.objects.get_or_create(
            village=village,
            source_name="Fictional Gravity Supply",
            defaults={
                "source_type": "piped",
                "ownership": "community",
                "operational_status": "operational",
                "capacity_litres": Decimal("25000"),
                "households_served": 41,
                "people_served": 205,
                "availability_status": "reliable",
                "average_days_unavailable_per_month": Decimal("1.5"),
                "water_quality_status": "safe",
                "last_water_test_date": measured,
                "condition": "good",
                "primary_or_backup": "primary",
            },
        )
        interruption_start = timezone.make_aware(datetime.combine(start + timedelta(days=45), datetime.min.time()))
        WaterInterruption.objects.get_or_create(
            report=report,
            water_source=water,
            start_date=interruption_start,
            defaults={
                "restored_date": interruption_start + timedelta(hours=6),
                "cause": "Fictional damaged intake pipe",
                "households_affected": 15,
                "people_affected": 66,
                "duration_hours": Decimal("6"),
                "responsible_agency": "Village Water Committee",
                "action_taken": "Pipe repaired and supply flushed.",
                "resolution_status": "resolved",
            },
        )
        WaterQualityTest.objects.get_or_create(
            water_source=water,
            test_date=measured,
            defaults={"tested_by": "Demo Health Inspector", "test_type": "Basic potability", "result": "Within fictional safe range", "safe_for_drinking": True},
        )
        WaterMaintenanceActivity.objects.get_or_create(
            report=report,
            water_source=water,
            activity_date=start + timedelta(days=47),
            defaults={"activity_type": "repair", "problem": "Damaged intake pipe", "action_taken": "Replaced coupling", "responsible_organisation": "Water Committee", "cost": Decimal("420"), "completion_status": "completed"},
        )

        SanitationSnapshot.objects.get_or_create(
            report=report,
            toilet_type="flush_septic",
            defaults={"functional_count": 38 + offset, "non_functional_count": 3, "shared_count": 7, "private_count": 34 + offset, "safely_managed_count": 35, "flood_vulnerable_count": 4, **analytical},
        )
        facility, _ = WasteFacility.objects.get_or_create(
            village=village,
            facility_type="community_collection_point",
            defaults={"operational_status": "operational", "collection_frequency": "weekly", "households_served": 41, "responsible_group": "Youth committee", "environmental_risk": "low", "last_inspection_date": measured},
        )
        WasteCollectionActivity.objects.get_or_create(
            report=report,
            facility=facility,
            collection_date=start + timedelta(days=50),
            defaults={"waste_type": "mixed recyclable", "estimated_volume": Decimal("3.5"), "measurement_unit": "cubic_metres", "collected_by": "Fictional council truck", "disposal_method": "approved facility"},
        )

        EnergySnapshot.objects.get_or_create(
            report=report,
            energy_source="electricity_grid",
            defaults={"households_connected": 39, "households_with_working_supply": 37, "average_hours_available_per_day": Decimal("22"), "average_days_unavailable_per_month": Decimal("1"), "primary_or_backup": "primary", "estimated_monthly_cost": Decimal("72"), **analytical},
        )
        VillageEnergyAsset.objects.get_or_create(
            village=village,
            asset_type="solar_street_lights",
            defaults={"capacity": Decimal("4.5"), "capacity_unit": "kW", "installation_date": date(2097, 8, 1), "households_served": 20, "ownership": "community", "condition": "good", "operational_status": "operational", "fuel_or_energy_type": "solar", "maintenance_provider": "Fictional Solar Cooperative"},
        )

        HealthConditionSnapshot.objects.get_or_create(
            report=report,
            health_condition=HealthCondition.objects.get(code="ari"),
            age_group=adult,
            gender="female",
            defaults={"new_cases": 4, "existing_cases": 3, "referred_cases": 2, "hospitalised_cases": 1, "recovered_cases": 4, "deaths": 0, **analytical},
        )
        VillageHealthAccessSnapshot.objects.get_or_create(
            report=report,
            defaults={"village_nurse_available": True, "nurse_visits_count": 18, "health_team_visits_count": 3, "nearest_health_facility": "Fictional Health Centre", "travel_time_minutes": 35, "transport_available": True, "medicine_shortage_days": 2, "emergency_referrals_count": 1, **analytical},
        )
        CommunitySafetyIncident.objects.get_or_create(
            report=report,
            village=village,
            offence_type=OffenceType.objects.get(code="theft"),
            incident_date=start + timedelta(days=52),
            defaults={"number_of_incidents": 1, "severity": "medium", "victim_age_group": adult, "victim_gender": "male", "reported_to_authority": True, "authority_reported_to": "Fictional Community Police", "report_date": start + timedelta(days=53), "action_taken": "Community awareness meeting held", "case_status": "under_review", **analytical},
        )
        DisabilitySnapshot.objects.get_or_create(
            report=report,
            disability_type=DisabilityType.objects.get(code="physical"),
            age_group=adult,
            gender="female",
            defaults={"count": 5, "receiving_support_count": 4, "attending_school_count": 1, "employed_count": 2, "support_required": "Accessible transport and mobility devices", **analytical},
        )

        CropProductionSnapshot.objects.get_or_create(
            report=report,
            crop_type=CropType.objects.get(code="dalo"),
            defaults={"number_of_farmers": 26, "number_of_gardens": 31, "area_planted": Decimal("8.5"), "area_unit": "hectares", "quantity_harvested": Decimal("4200"), "quantity_unit": "kg", "quantity_consumed": Decimal("1700"), "quantity_sold": Decimal("2200"), "quantity_lost": Decimal("300"), "estimated_sales_value": Decimal("13200"), "planting_season": "year_round", **analytical},
        )
        FoodSecuritySnapshot.objects.get_or_create(
            report=report,
            defaults={"households_with_food_shortage": 4, "average_food_shortage_days": Decimal("3"), "main_cause": "Fictional storm disruption", "external_assistance_received": True, "assistance_provider": "Demo relief programme", **analytical},
        )

        business, _ = VillageBusiness.objects.get_or_create(
            village=village,
            business_name="Fictional Women's Catering Cooperative",
            defaults={"business_sector": "hospitality", "owner_type": "cooperative", "owner_name": "Fictional Women's Group", "owner_gender": "female", "owner_age_group": adult, "start_date": date(2097, 2, 1), "licence_status": "current", "operating_status": "operating", "full_time_employees": 4, "part_time_employees": 6, "male_employees": 2, "female_employees": 8, "youth_employees": 3, "revenue_band": "10000_25000", "primary_market": "local and nearby towns", "support_required": "Food-safety certification support"},
        )
        account, _ = VillageFinancialAccount.objects.get_or_create(
            village=village,
            account_type="development_fund",
            defaults={"institution": "Fictional Community Bank", "account_purpose": "Village development projects", "opening_date": date(2096, 1, 1), "authorised_signatories_count": 3},
        )
        VillageFinancialSnapshot.objects.get_or_create(
            account=account,
            report=report,
            defaults={"opening_balance": Decimal("12000"), "deposits": Decimal("5500"), "withdrawals": Decimal("3200"), "interest_or_return": Decimal("50"), "closing_balance": Decimal("14350"), "verified_from_statement": True},
        )

        project, _ = IVDPProject.objects.get_or_create(
            village=village,
            project_code=f"{village.code}-WATER-01",
            defaults={"project_name": "Fictional water resilience upgrade", "project_category": "water", "problem_being_addressed": "Dry-season supply interruptions", "baseline_value": Decimal("4"), "target_value": Decimal("1"), "measurement_unit": "outage_days", "priority": "high", "responsible_person": str(person), "responsible_organisation": "Village Water Committee", "planned_start_date": date(2099, 1, 1), "planned_end_date": date(2099, 12, 31), "actual_start_date": date(2099, 1, 15), "estimated_budget": Decimal("48000"), "approved_budget": Decimal("45000"), "actual_expenditure": Decimal("18000") + offset, "funding_source": "Fictional rural development fund", "project_status": "in_progress", "physical_progress_percentage": Decimal("45") + offset, "financial_progress_percentage": Decimal("40"), "expected_beneficiaries": 210, "male_beneficiaries": 98, "female_beneficiaries": 104, "youth_beneficiaries": 65},
        )
        milestone, _ = ProjectMilestone.objects.get_or_create(
            project=project,
            title="Install communal storage tanks",
            defaults={"planned_date": date(2099, 8, 31), "percentage_weight": Decimal("35"), "status": "in_progress"},
        )
        IVDPProjectProgress.objects.get_or_create(
            project=project,
            report=report,
            defaults={"reporting_date": measured, "work_completed": "Tank bases completed and materials delivered.", "milestone": milestone, "progress_percentage": Decimal("45") + offset, "expenditure_to_date": Decimal("18000") + offset, "materials_received": "Cement, aggregate, fittings and two tanks", "challenges": "Weather delayed transport", "corrective_action": "Revised delivery schedule", "next_activity": "Install and connect tanks", "next_activity_due_date": date(2099, 8, 31), "risk_level": "medium"},
        )
        ProjectRisk.objects.get_or_create(
            project=project,
            risk_type="delivery_delay",
            defaults={"description": "Wet-weather road access may delay materials.", "likelihood": "medium", "impact": "medium", "mitigation": "Pre-position critical materials.", "owner": "Project Committee", "status": "open"},
        )

        ClimateImpactObservation.objects.get_or_create(
            report=report,
            village=village,
            hazard_type="coastal_flooding",
            observation_date=start + timedelta(days=55),
            defaults={"severity": "medium", "frequency": "seasonal", "households_affected": 6, "population_affected": 27, "farmland_affected": Decimal("1.5"), "infrastructure_affected": "Fictional coastal footpath", "estimated_damage_value": Decimal("3500"), "description": "King tide caused temporary access disruption."},
        )
        VillageDisasterPreparedness.objects.get_or_create(
            village=village,
            defaults={"disaster_plan_available": True, "plan_last_updated": date(2099, 1, 10), "disaster_committee_active": True, "emergency_contacts_available": True, "evacuation_drill_date": start + timedelta(days=32), "warning_system_available": True, "emergency_supplies_available": True, "vulnerable_people_register_available": True, "last_reviewed": measured},
        )
        EvacuationCentre.objects.get_or_create(
            village=village,
            name="Fictional Community Evacuation Hall",
            defaults={"building_material": "reinforced_concrete", "capacity": 220, "separate_male_female_restrooms": True, "accessibility_status": "accessible", "water_available": True, "sanitation_available": True, "condition": "good"},
        )
        DisasterIncident.objects.get_or_create(
            report=report,
            village=village,
            incident_type="severe_storm",
            incident_date=start + timedelta(days=58),
            defaults={"warning_received": True, "people_evacuated": 18, "injuries": 0, "deaths": 0, "houses_damaged": 2, "houses_destroyed": 0, "estimated_loss": Decimal("6000"), "response_time_minutes": 35, "assistance_received": True, "assistance_provider": "Demo Provincial Office"},
        )

        unit, _ = TraditionalUnit.objects.get_or_create(
            village=village, unit_type="mataqali", name=f"Fictional Mataqali {village.code}"
        )
        TraditionalTitle.objects.get_or_create(
            traditional_unit=unit,
            title_name="Fictional Turaga Title",
            defaults={"title_type": "chiefly", "status": "filled", "confirmation_stage": "confirmed", "confirmation_date": date(2098, 3, 1), "next_action": "Annual record review", "responsible_party": "Village Council"},
        )
        CulturalKnowledgeRecord.objects.get_or_create(
            village=village,
            knowledge_name="Fictional traditional planting calendar",
            defaults={"knowledge_category": "agriculture", "description": "Demonstration description of seasonal planting knowledge.", "number_of_knowledge_holders": 12, "youngest_knowledge_holder_age": 29, "transmission_status": "active", "preservation_activity": "Quarterly youth learning sessions", "activity_frequency": "quarterly", "youth_participation": True, "documentation_available": True, "risk_level": "secure"},
        )
        return business

    def _evidence(self, report, user):
        document = EvidenceDocument(
            title=f"Fictional minutes - {report.village.code} - {report.reporting_period}",
            document_type="meeting_minutes",
            file=SimpleUploadedFile(
                f"demo-{report.village.code}-{report.reporting_period.year}-q{report.reporting_period.quarter}.pdf",
                b"%PDF-1.4\n% Fictional TNK demonstration evidence only\n%%EOF\n",
                content_type="application/pdf",
            ),
            original_filename="fictional-demo-minutes.pdf",
            file_size=58,
            mime_type="application/pdf",
            checksum="0" * 64,
            description="Synthetic evidence created by seed_demo_data; it contains no real information.",
            confidentiality_level="restricted",
            uploaded_by=user,
        )
        document.full_clean()
        document.save()
        EvidenceLink.objects.create(document=document, content_object=report)

    def _complete(self, report, user):
        report.section_statuses.update(
            status=ReportSectionStatus.Status.COMPLETE,
            completion_percentage=Decimal("100"),
            last_updated_by=user,
        )
        FinalDeclaration.objects.create(
            report=report,
            declared_by=user,
            declaration_text="I confirm this is complete fictional demonstration data.",
            acknowledged=True,
        )

    def _print_credentials(self, users, show):
        if not show:
            return
        self.stdout.write("\nFictional demo login accounts (all use the same password):")
        for key, user in users.items():
            self.stdout.write(f"  {key:12} {user.username}")
        self.stdout.write(f"  password     {DEMO_PASSWORD}")
        self.stdout.write("Use these accounts only in local development, then remove the demo database before deployment.")
