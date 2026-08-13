from datetime import date
from calendar import monthrange
from django.core.management.base import BaseCommand,CommandError
from apps.reporting.models import ReportingPeriod
class Command(BaseCommand):
    help="Create a validated quarterly reporting period."
    def add_arguments(self,p): p.add_argument("year",type=int); p.add_argument("quarter",type=int); p.add_argument("--due-date",required=True); p.add_argument("--open",action="store_true")
    def handle(self,*args,**o):
        year=o["year"]; quarter=o["quarter"]; start_month=(quarter-1)*3+1
        try: due=date.fromisoformat(o["due_date"]); end_month=start_month+2; obj=ReportingPeriod(year=year,quarter=quarter,start_date=date(year,start_month,1),end_date=date(year,end_month,monthrange(year,end_month)[1]),submission_due_date=due,is_open=o["open"]); obj.full_clean(); obj.save()
        except Exception as exc: raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS(str(obj)))
