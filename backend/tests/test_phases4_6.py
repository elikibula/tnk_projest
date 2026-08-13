from datetime import date
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.test import TestCase
from apps.accounts.models import User
from apps.economy.models import VillageFinancialAccount,VillageFinancialSnapshot
from apps.locations.models import Province,Tikina,Village
from apps.projects.models import IVDPProject
from apps.reporting.models import ReportingPeriod,TNKReport
class ServiceDomainTests(TestCase):
    def setUp(self):
        p=Province.objects.create(code="LAU",name_en="Lau"); t=Tikina.objects.create(province=p,code="LAK",name_en="Lakeba"); self.v=Village.objects.create(tikina=t,code="TUB",name_en="Tubou"); u=User.objects.create_user(username="u"); rp=ReportingPeriod.objects.create(year=2026,quarter=1,start_date=date(2026,1,1),end_date=date(2026,3,31),submission_due_date=date(2026,4,10)); self.r=TNKReport.objects.create(village=self.v,reporting_period=rp,prepared_by=u,collection_started_at="2026-01-01T00:00:00Z")
    def test_financial_snapshot_must_reconcile(self):
        account=VillageFinancialAccount.objects.create(village=self.v,account_type="development",institution="Bank",account_purpose="Projects")
        bad=VillageFinancialSnapshot(account=account,report=self.r,opening_balance=Decimal("100"),deposits=Decimal("20"),withdrawals=Decimal("10"),interest_or_return=Decimal("1"),closing_balance=Decimal("99"))
        with self.assertRaises(ValidationError): bad.full_clean()
    def test_completed_project_requires_completion_date(self):
        project=IVDPProject(project_code="P1",village=self.v,project_name="Water",project_category="water",problem_being_addressed="Access",priority="high",project_status="completed")
        with self.assertRaises(ValidationError): project.full_clean()
    def test_health_models_do_not_contain_patient_name_fields(self):
        from apps.wellbeing.models import HealthConditionSnapshot,DisabilitySnapshot
        names={f.name for m in (HealthConditionSnapshot,DisabilitySnapshot) for f in m._meta.fields}
        self.assertNotIn("patient_name",names); self.assertNotIn("full_name",names)
