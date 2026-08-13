from django.db import models
from django.db.models import Sum
from .models import Household, PopulationSnapshot

def verified_population_for_village(village):
    report_id = PopulationSnapshot.objects.filter(village=village, verification_status=PopulationSnapshot.VerificationStatus.VERIFIED).order_by("-report__reporting_period__end_date").values_list("report_id", flat=True).first()
    if report_id is None: return None
    return PopulationSnapshot.objects.filter(report_id=report_id, village=village, verification_status=PopulationSnapshot.VerificationStatus.VERIFIED).aggregate(total=Sum("count"))["total"]

def household_aggregates_for_village(village):
    return Household.objects.filter(village=village, is_active=True).aggregate(households=models.Count("pk"), people=Sum("household_size"))
