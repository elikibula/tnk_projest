from datetime import date
from django.core.exceptions import ValidationError
from django.test import TestCase
from apps.accounts.models import User
from apps.governance.models import OfficialAppointment, OfficialRole, PersonReference
from apps.locations.models import Province, Tikina, Village
from apps.population.models import AgeGroup, Household, PopulationMovement, PopulationSnapshot
from apps.population.selectors import verified_population_for_village
from apps.reporting.models import ReportingPeriod, TNKReport

class Phase3DomainTests(TestCase):
    def setUp(self):
        province=Province.objects.create(code="LAU",name_en="Lau"); tikina=Tikina.objects.create(province=province,code="LAK",name_en="Lakeba"); self.village=Village.objects.create(tikina=tikina,code="TUB",name_en="Tubou")
        self.user=User.objects.create_user(username="author"); self.period=ReportingPeriod.objects.create(year=2026,quarter=1,start_date=date(2026,1,1),end_date=date(2026,3,31),submission_due_date=date(2026,4,10)); self.report=TNKReport.objects.create(village=self.village,reporting_period=self.period,prepared_by=self.user,collection_started_at="2026-01-01T00:00:00Z"); self.age_group=AgeGroup.objects.create(code="25_34",name_en="25-34",minimum_age=25,maximum_age=34)
    def test_verified_population_is_source_of_truth(self):
        for gender,count in (("female",12),("male",10)): PopulationSnapshot.objects.create(report=self.report,village=self.village,age_group=self.age_group,gender=gender,resident_status="permanent_resident",count=count,measurement_date=date(2026,3,31),data_source="physical_count",collection_method="census",verification_status="verified")
        self.assertEqual(verified_population_for_village(self.village),22)
    def test_movement_is_separate_from_snapshot(self):
        PopulationMovement.objects.create(village=self.village,reporting_period=self.period,movement_type="birth",movement_date=date(2026,2,1),count=1,data_source="village_register"); self.assertEqual(PopulationSnapshot.objects.count(),0)
    def test_household_history_uses_effective_records(self):
        first=Household.objects.create(household_code="H1",village=self.village,household_head_name="A",effective_from=date(2025,1,1),effective_to=date(2025,12,31),is_active=False); current=Household.objects.create(household_code="H1",village=self.village,household_head_name="A",effective_from=date(2026,1,1)); self.assertNotEqual(first.uuid,current.uuid)
    def test_current_official_cannot_have_end_date(self):
        person=PersonReference.objects.create(full_name="Official",home_village=self.village); role=OfficialRole.objects.create(code="tnk",name_en="Turaga ni Koro"); appointment=OfficialAppointment(person=person,village=self.village,role=role,appointment_date=date(2026,1,1),effective_from=date(2026,1,1),effective_to=date(2026,2,1),is_current=True)
        with self.assertRaises(ValidationError): appointment.full_clean()
