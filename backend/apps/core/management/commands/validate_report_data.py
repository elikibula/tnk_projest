from django.core.management.base import BaseCommand,CommandError
from apps.data_quality.services import validate_report
from apps.reporting.models import TNKReport
class Command(BaseCommand):
    help="Validate one report by public UUID."
    def add_arguments(self,p): p.add_argument("report_uuid")
    def handle(self,*args,**o):
        try: report=TNKReport.objects.get(uuid=o["report_uuid"])
        except TNKReport.DoesNotExist as exc: raise CommandError("Report not found.") from exc
        issues=validate_report(report); self.stdout.write(f"{issues.count()} unresolved issues; score {report.data_quality_score}")
