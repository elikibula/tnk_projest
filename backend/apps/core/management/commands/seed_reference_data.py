from django.core.management.base import BaseCommand
from django.db import transaction
from apps.accounts.models import Role
from apps.analytics.services import seed_indicator_definitions
from apps.population.models import AgeGroup
from apps.governance.models import OfficialRole
from apps.wellbeing.models import DisabilityType, HealthCondition, OffenceType
from apps.economy.models import CropType
class Command(BaseCommand):
    help="Seed controlled, non-personal reference data."
    @transaction.atomic
    def handle(self,*args,**options):
        for code,label in Role.Codes.choices: Role.objects.update_or_create(code=code,defaults={"name":label,"is_active":True})
        groups=(("0_4","0-4",0,4),("5_9","5-9",5,9),("10_14","10-14",10,14),("15_19","15-19",15,19),("20_24","20-24",20,24),("25_34","25-34",25,34),("35_44","35-44",35,44),("45_54","45-54",45,54),("55_64","55-64",55,64),("65_plus","65+",65,None))
        for order,(code,name,minimum,maximum) in enumerate(groups): AgeGroup.objects.update_or_create(code=code,defaults={"name_en":name,"minimum_age":minimum,"maximum_age":maximum,"sort_order":order})
        official_roles=(("turaga_ni_koro","Turaga ni Koro"),("village_headwoman","Village Headwoman"),("committee_chair","Committee Chairperson"),("committee_secretary","Committee Secretary"),("treasurer","Treasurer"))
        for code,name in official_roles: OfficialRole.objects.update_or_create(code=code,defaults={"name_en":name})
        health_conditions=(("ari","Acute respiratory infection","communicable",True),("diarrhoea","Diarrhoeal illness","communicable",True),("diabetes","Diabetes","non_communicable",False),("hypertension","Hypertension","non_communicable",False),("other","Other condition","other",False))
        for code,name,category,communicable in health_conditions: HealthCondition.objects.update_or_create(code=code,defaults={"name_en":name,"category":category,"is_communicable":communicable,"is_active":True})
        disability_types=(("physical","Physical disability","physical"),("visual","Visual impairment","sensory"),("hearing","Hearing impairment","sensory"),("intellectual","Intellectual disability","intellectual"),("psychosocial","Psychosocial disability","psychosocial"),("other","Other disability","other"))
        for code,name,category in disability_types: DisabilityType.objects.update_or_create(code=code,defaults={"name_en":name,"category":category,"is_active":True})
        offences=(("theft","Theft","property","medium"),("assault","Assault","violence","high"),("domestic_violence","Domestic violence","violence","high"),("drug_related","Drug-related incident","drugs","high"),("other","Other incident","other","medium"))
        for code,name,category,severity in offences: OffenceType.objects.update_or_create(code=code,defaults={"name_en":name,"category":category,"default_severity":severity,"is_active":True})
        crops=(("dalo","Dalo","root_crop","kg"),("cassava","Cassava","root_crop","kg"),("yam","Yam","root_crop","kg"),("kava","Kava","cash_crop","kg"),("coconut","Coconut","tree_crop","count"),("vegetables","Vegetables","horticulture","kg"),("other","Other crop","other","kg"))
        for code,name,group,unit in crops: CropType.objects.update_or_create(code=code,defaults={"name_en":name,"crop_group":group,"default_measurement_unit":unit})
        seed_indicator_definitions(); self.stdout.write(self.style.SUCCESS("Reference data seeded."))
