from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Role, User, UserLocationAssignment, UserRoleAssignment
from apps.analytics.decision_support import location_rows, percentage_change, reporting_summary, summary
from apps.analytics.models import IndicatorDefinition, IndicatorValue
from apps.locations.models import Province, Tikina, Village
from apps.reporting.models import ReportingPeriod, TNKReport


class DecisionAnalyticsTests(TestCase):
    def setUp(self):
        self.period1 = ReportingPeriod.objects.create(year=2026, quarter=1, start_date=date(2026, 1, 1), end_date=date(2026, 3, 31), submission_due_date=date(2026, 4, 15))
        self.period2 = ReportingPeriod.objects.create(year=2026, quarter=2, start_date=date(2026, 4, 1), end_date=date(2026, 6, 30), submission_due_date=date(2026, 7, 15), is_open=True)
        self.province_a = Province.objects.create(code="DA-A", name_en="Analytics Province A")
        self.province_b = Province.objects.create(code="DA-B", name_en="Analytics Province B")
        self.tikina_a = Tikina.objects.create(province=self.province_a, code="DA-TA", name_en="Analytics Tikina A")
        self.tikina_b = Tikina.objects.create(province=self.province_b, code="DA-TB", name_en="Analytics Tikina B")
        self.village_a1 = Village.objects.create(tikina=self.tikina_a, code="DA-A1", name_en="Analytics Village A1")
        self.village_a2 = Village.objects.create(tikina=self.tikina_a, code="DA-A2", name_en="Analytics Village A2")
        self.village_b = Village.objects.create(tikina=self.tikina_b, code="DA-B1", name_en="Analytics Village B")
        self.system = self.user("analytics-system", Role.Codes.SYSTEM_ADMIN)
        self.provincial = self.user("analytics-provincial", Role.Codes.PROVINCIAL_ADMIN, province=self.province_a)
        self.author = self.user("analytics-author", Role.Codes.TURAGA_NI_KORO, village=self.village_a1)
        self.untrusted = User.objects.create_user(username="analytics-no-role")
        self.population = self.definition("total_population", "people")
        self.households = self.definition("average_household_size", "people per household")
        self.water = self.definition("water_failure_count", "interruptions")

    def user(self, username, role_code, **location):
        user = User.objects.create_user(username=username, password="test-password")
        role, _ = Role.objects.get_or_create(code=role_code, defaults={"name": Role(code=role_code).get_code_display()})
        UserRoleAssignment.objects.create(user=user, role=role)
        if location:
            UserLocationAssignment.objects.create(user=user, **location)
        return user

    def definition(self, code, unit):
        return IndicatorDefinition.objects.create(code=code, name_en=code.replace("_", " ").title(), description="Test", formula_description="Test formula", measurement_unit=unit, geographic_level="village", effective_from=date(2026, 1, 1))

    def report(self, village, period, status=TNKReport.Status.APPROVED):
        return TNKReport.objects.create(village=village, reporting_period=period, prepared_by=self.author, collection_started_at="2026-01-01T00:00:00Z", status=status)

    def value(self, indicator, village, period, value, numerator=None, denominator=None):
        return IndicatorValue.objects.create(indicator=indicator, reporting_period=period, province=village.tikina.province, tikina=village.tikina, village=village, value=value, numerator_value=numerator, denominator_value=denominator)

    def test_percentage_change_handles_missing_and_zero_safely(self):
        self.assertIsNone(percentage_change(None, 1))
        self.assertIsNone(percentage_change(0, 10))
        self.assertEqual(percentage_change(0, 0), 0)
        self.assertEqual(percentage_change(100, 125), 25)

    def test_national_total_equals_province_totals_without_aggregate_double_counting(self):
        for village, population in ((self.village_a1, 10), (self.village_a2, 20), (self.village_b, 30)):
            self.report(village, self.period2)
            self.value(self.population, village, self.period2, population)
        IndicatorValue.objects.create(indicator=self.population, reporting_period=self.period2, province=self.province_a, value=Decimal("999"))
        national = summary(self.system, self.period2)
        province_rows = location_rows(self.system, self.period2)
        self.assertEqual(national["indicators"]["population"]["value"], Decimal("60"))
        self.assertEqual(sum(row["indicators"]["population"]["value"] for row in province_rows), Decimal("60"))

    def test_province_tikina_and_village_aggregation_are_strictly_scoped(self):
        self.value(self.population, self.village_a1, self.period2, 10)
        self.value(self.population, self.village_a2, self.period2, 20)
        self.value(self.population, self.village_b, self.period2, 500)
        self.assertEqual(summary(self.system, self.period2, self.province_a)["indicators"]["population"]["value"], 30)
        self.assertEqual(summary(self.system, self.period2, self.tikina_a)["indicators"]["population"]["value"], 30)
        self.assertEqual(summary(self.system, self.period2, self.village_a1)["indicators"]["population"]["value"], 10)

    def test_zero_is_data_while_absent_indicator_is_missing(self):
        self.value(self.water, self.village_a1, self.period2, 0)
        current = summary(self.system, self.period2, self.village_a1)
        self.assertTrue(current["indicators"]["water_issues"]["has_data"])
        self.assertEqual(current["indicators"]["water_issues"]["value"], 0)
        self.assertFalse(current["indicators"]["population"]["has_data"])
        self.assertIsNone(current["indicators"]["population"]["value"])

    def test_reporting_compliance_counts_distinct_workflow_states_and_missing(self):
        self.report(self.village_a1, self.period2, TNKReport.Status.SUBMITTED)
        result = reporting_summary(self.provincial, self.period2, self.province_a)
        self.assertEqual(result["expected"], 2)
        self.assertEqual(result["received"], 1)
        self.assertEqual(result["official"], 0)
        self.assertEqual(result["missing"], 1)
        self.assertEqual(result["completion"], Decimal("50.0"))

    def test_permissions_and_provincial_url_scope_are_enforced(self):
        self.client.force_login(self.untrusted)
        self.assertEqual(self.client.get(reverse("analytics:dashboard")).status_code, 403)
        self.client.force_login(self.provincial)
        self.assertEqual(self.client.get(reverse("analytics:dashboard")).status_code, 200)
        self.assertEqual(self.client.get(reverse("analytics:national")).status_code, 403)
        self.assertEqual(self.client.get(reverse("analytics:province", args=(self.province_b.uuid,))).status_code, 404)
        response = self.client.get(reverse("analytics:dashboard"))
        self.assertContains(response, self.province_a.name_en)
        self.assertNotContains(response, self.province_b.name_en)

    def test_system_has_national_drilldown_and_period_filter(self):
        self.value(self.population, self.village_a1, self.period1, 10)
        self.value(self.population, self.village_a1, self.period2, 25)
        self.client.force_login(self.system)
        response = self.client.get(reverse("analytics:national"), {"period": self.period1.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_period"], self.period1)
        self.assertContains(response, "Fiji National Analytics")
        self.assertEqual(self.client.get(reverse("analytics:province", args=(self.province_a.uuid,))).status_code, 200)
        self.assertEqual(self.client.get(reverse("analytics:tikina", args=(self.tikina_a.uuid,))).status_code, 200)
        self.assertEqual(self.client.get(reverse("analytics:village", args=(self.village_a1.uuid,))).status_code, 200)
        self.assertEqual(self.client.get(reverse("analytics:data_quality"), {"period": self.period2.pk}).status_code, 200)

    def test_comparison_is_limited_to_authorised_locations(self):
        self.client.force_login(self.provincial)
        response = self.client.get(reverse("analytics:compare"), {"level": "province", "period": self.period2.pk, "locations": [self.province_a.pk, self.province_b.pk]})
        self.assertEqual(len(response.context["selected"]), 1)
        self.assertEqual(response.context["selected"][0]["location"], self.province_a)

    def test_missing_report_view_and_scoped_csv_export(self):
        self.report(self.village_a1, self.period2)
        self.client.force_login(self.provincial)
        response = self.client.get(reverse("analytics:reporting"), {"period": self.period2.pk})
        self.assertContains(response, self.village_a2.name_en)
        self.assertNotContains(response, self.village_b.name_en)
        export = self.client.get(reverse("analytics:summary_export"), {"period": self.period2.pk, "scope_type": "province", "scope": self.province_a.uuid})
        self.assertEqual(export.status_code, 200)
        text = export.content.decode("utf-8-sig")
        self.assertIn(self.tikina_a.name_en, text)
        self.assertNotIn(self.tikina_b.name_en, text)
