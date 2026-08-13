from django.core.management.base import BaseCommand
from apps.data_quality.services import validate_report
from apps.reporting.models import TNKReport
class Command(BaseCommand):
    help="Recalculate report data-quality issues and scores."
    def handle(self,*args,**options):
        for report in TNKReport.objects.exclude(status="archived"): validate_report(report)
        self.stdout.write(self.style.SUCCESS("Data-quality scores recalculated."))
