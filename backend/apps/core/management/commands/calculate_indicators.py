from django.core.management.base import BaseCommand
from apps.analytics.services import calculate_period_indicators, seed_indicator_definitions
from apps.reporting.models import ReportingPeriod
class Command(BaseCommand):
    help="Calculate the approved indicator catalogue for official reports at village, Tikina, and province levels."
    def handle(self,*args,**options):
        seed_indicator_definitions()
        count=sum(len(calculate_period_indicators(period)) for period in ReportingPeriod.objects.all())
        self.stdout.write(self.style.SUCCESS(f"Calculated {count} indicator values."))
