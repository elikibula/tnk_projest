from datetime import date
from decimal import Decimal

from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Role, User, UserLocationAssignment, UserRoleAssignment
from apps.analytics.models import IndicatorValue
from apps.analytics.services import aggregate_indicators, seed_indicator_definitions
from apps.locations.models import Province, Tikina, Village
from apps.reporting.amendments import (
    add_amendment_change,
    apply_indicator_overrides,
    authoritative_changes,
    create_amendment,
    transition_amendment,
)
from apps.reporting.models import ReportAmendment, ReportingPeriod, TNKReport
from apps.reporting.services import create_report


class ReportAmendmentTests(TestCase):
    def setUp(self):
        self.province = Province.objects.create(code="AMD", name_en="Amendment Province")
        self.tikina = Tikina.objects.create(province=self.province, code="AMD-T", name_en="Amendment Tikina")
        self.village = Village.objects.create(tikina=self.tikina, code="AMD-V", name_en="Original Village Name")
        self.other_village = Village.objects.create(tikina=self.tikina, code="AMD-O", name_en="Other Village")
        self.period = ReportingPeriod.objects.create(
            year=2026,
            quarter=3,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 9, 30),
            submission_due_date=date(2026, 10, 15),
            is_open=True,
        )
        self.requester = self.make_user("requester", Role.Codes.TURAGA_NI_KORO, village=self.village)
        self.reviewer = self.make_user("reviewer", Role.Codes.ROKO_TUI, province=self.province)
        self.outsider = self.make_user("outsider", Role.Codes.TURAGA_NI_KORO, village=self.other_village)
        self.report = create_report(village=self.village, reporting_period=self.period, prepared_by=self.requester)
        TNKReport.objects.filter(pk=self.report.pk).update(status=TNKReport.Status.APPROVED)
        self.report.refresh_from_db()

    @staticmethod
    def make_user(username, role_code, **location):
        user = User.objects.create_user(username=username, password="test-password")
        role, _ = Role.objects.get_or_create(code=role_code, defaults={"name": Role(code=role_code).get_code_display()})
        UserRoleAssignment.objects.create(user=user, role=role)
        UserLocationAssignment.objects.create(user=user, **location)
        return user

    def create_change(self, amendment, *, amended_value="Corrected Village Name", **analytics):
        return add_amendment_change(
            amendment=amendment,
            user=self.requester,
            section_code="village_profile",
            entry_key="village",
            source_identifier=self.village.uuid,
            field_name="name_en",
            amended_value=amended_value,
            change_reason="The approved name contains a transcription error.",
            **analytics,
        )

    def approved_amendment(self, *, amended_value="Corrected Village Name"):
        amendment = create_amendment(report=self.report, user=self.requester, reason="Correct a confirmed transcription error.")
        self.create_change(amendment, amended_value=amended_value)
        transition_amendment(amendment=amendment, user=self.requester, action="submit")
        return transition_amendment(amendment=amendment, user=self.reviewer, action="approve", acknowledged=True)

    def test_only_official_reports_can_be_amended_and_requester_must_be_in_scope(self):
        TNKReport.objects.filter(pk=self.report.pk).update(status=TNKReport.Status.DRAFT)
        self.report.refresh_from_db()
        with self.assertRaisesMessage(ValidationError, "approved, locked, or archived"):
            create_amendment(report=self.report, user=self.requester, reason="Correction required")
        TNKReport.objects.filter(pk=self.report.pk).update(status=TNKReport.Status.APPROVED)
        self.report.refresh_from_db()
        with self.assertRaises(PermissionDenied):
            create_amendment(report=self.report, user=self.outsider, reason="Correction required")

    def test_original_value_is_resolved_server_side_and_original_report_stays_unchanged(self):
        amendment = create_amendment(report=self.report, user=self.requester, reason="Correct the village name")
        change = self.create_change(amendment)
        self.assertEqual(change.original_value, "Original Village Name")
        self.approved_amendment(amended_value="Authoritative Name")
        self.village.refresh_from_db()
        self.report.refresh_from_db()
        self.assertEqual(self.village.name_en, "Original Village Name")
        self.assertEqual(self.report.status, TNKReport.Status.APPROVED)

    def test_submission_freezes_amendment_and_change_records(self):
        amendment = create_amendment(report=self.report, user=self.requester, reason="Correct the village name")
        change = self.create_change(amendment)
        transition_amendment(amendment=amendment, user=self.requester, action="submit")
        amendment.refresh_from_db()
        amendment.reason = "Tampered"
        with self.assertRaisesMessage(ValidationError, "immutable"):
            amendment.save()
        change.amended_value = "Tampered"
        with self.assertRaisesMessage(ValidationError, "immutable"):
            change.save()
        with self.assertRaisesMessage(ValidationError, "immutable"):
            amendment.changes.update(amended_value="Tampered")
        with self.assertRaisesMessage(ValidationError, "immutable"):
            change.delete()

    def test_independent_approval_acknowledgement_and_rejection_reason_are_enforced(self):
        amendment = create_amendment(report=self.report, user=self.requester, reason="Correct the village name")
        self.create_change(amendment)
        transition_amendment(amendment=amendment, user=self.requester, action="submit")
        reviewer_role = Role.objects.get(code=Role.Codes.ROKO_TUI)
        UserRoleAssignment.objects.create(user=self.requester, role=reviewer_role)
        with self.assertRaisesMessage(PermissionDenied, "cannot approve their own"):
            transition_amendment(amendment=amendment, user=self.requester, action="approve", acknowledged=True)
        with self.assertRaisesMessage(ValidationError, "Acknowledge"):
            transition_amendment(amendment=amendment, user=self.reviewer, action="approve")
        with self.assertRaisesMessage(ValidationError, "Explain why"):
            transition_amendment(amendment=amendment, user=self.reviewer, action="reject")

    def test_latest_approved_correction_is_authoritative_per_field(self):
        first = self.approved_amendment(amended_value="First Correction")
        second = self.approved_amendment(amended_value="Second Correction")
        changes = authoritative_changes(self.report)
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].amended_value, "Second Correction")
        self.assertEqual(changes[0].amendment_id, second.pk)
        self.assertTrue(second.supersedes_previous)
        self.assertEqual(second.supersedes_amendment_id, first.pk)

    def test_approved_indicator_override_is_authoritative_and_reaggregated(self):
        definition = {item.code: item for item in seed_indicator_definitions()}["total_population"]
        original = IndicatorValue.objects.create(
            indicator=definition,
            reporting_period=self.period,
            province=self.province,
            tikina=self.tikina,
            village=self.village,
            value=Decimal("10"),
            numerator_value=Decimal("10"),
            calculation_status=IndicatorValue.CalculationStatus.CALCULATED,
        )
        IndicatorValue.objects.create(
            indicator=definition,
            reporting_period=self.period,
            province=self.province,
            tikina=self.tikina,
            village=self.other_village,
            value=Decimal("5"),
            numerator_value=Decimal("5"),
            calculation_status=IndicatorValue.CalculationStatus.CALCULATED,
        )
        amendment = create_amendment(report=self.report, user=self.requester, reason="Correct the population total")
        self.create_change(
            amendment,
            amended_value="Population register correction",
            indicator_code="total_population",
            amended_indicator_value=Decimal("12"),
            amended_indicator_numerator=Decimal("12"),
        )
        transition_amendment(amendment=amendment, user=self.requester, action="submit")
        transition_amendment(amendment=amendment, user=self.reviewer, action="approve", acknowledged=True)
        original.refresh_from_db()
        self.assertEqual(original.value, Decimal("10"))
        overlaid = apply_indicator_overrides([original])[0]
        self.assertEqual(overlaid.authoritative_value, Decimal("12"))
        aggregate = aggregate_indicators(self.period, self.tikina)
        total = next(value for value in aggregate if value.indicator.code == "total_population")
        self.assertEqual(total.value, Decimal("17"))

    def test_rate_override_must_match_its_numerator_and_denominator(self):
        definition = {item.code: item for item in seed_indicator_definitions()}["active_committee_rate"]
        IndicatorValue.objects.create(
            indicator=definition,
            reporting_period=self.period,
            province=self.province,
            tikina=self.tikina,
            village=self.village,
            value=Decimal("50"),
            numerator_value=Decimal("1"),
            denominator_value=Decimal("2"),
            calculation_status=IndicatorValue.CalculationStatus.CALCULATED,
        )
        amendment = create_amendment(report=self.report, user=self.requester, reason="Correct a committee rate")
        with self.assertRaisesMessage(ValidationError, "does not match"):
            self.create_change(
                amendment,
                amended_value="Committee register correction",
                indicator_code="active_committee_rate",
                amended_indicator_value=Decimal("80"),
                amended_indicator_numerator=Decimal("3"),
                amended_indicator_denominator=Decimal("5"),
            )

    def test_browser_workflow_shows_original_corrected_and_human_errors(self):
        self.client.force_login(self.requester)
        response = self.client.post(
            reverse("reporting:amendment_create", args=(self.report.uuid,)),
            {"reason": "Correct a confirmed name error", "notes": "Register checked"},
        )
        self.assertEqual(response.status_code, 302)
        amendment = ReportAmendment.objects.get()
        response = self.client.post(
            reverse("reporting:amendment_change_create", args=(amendment.uuid,)),
            {
                "section_code": "village_profile",
                "entry_key": "village",
                "source_identifier": self.village.uuid,
                "field_name": "name_en",
                "amended_value": "Corrected Village Name",
                "change_reason": "Register confirmed the correct spelling",
            },
        )
        self.assertRedirects(response, reverse("reporting:amendment_detail", args=(amendment.uuid,)))
        detail = self.client.get(reverse("reporting:amendment_detail", args=(amendment.uuid,)))
        self.assertContains(detail, "Original Village Name")
        self.assertContains(detail, "Corrected Village Name")
        self.client.post(reverse("reporting:amendment_action", args=(amendment.uuid, "submit")))
        self.client.force_login(self.reviewer)
        response = self.client.post(reverse("reporting:amendment_action", args=(amendment.uuid, "approve")), follow=True)
        self.assertContains(response, "Acknowledge the amendment approval")

    def test_out_of_scope_and_get_workflow_requests_are_denied(self):
        amendment = create_amendment(report=self.report, user=self.requester, reason="Correct the village name")
        self.client.force_login(self.outsider)
        self.assertEqual(self.client.get(reverse("reporting:amendment_detail", args=(amendment.uuid,))).status_code, 404)
        self.assertEqual(self.client.post(reverse("reporting:amendment_action", args=(amendment.uuid, "submit"))).status_code, 404)
        self.client.force_login(self.requester)
        self.assertEqual(self.client.get(reverse("reporting:amendment_action", args=(amendment.uuid, "submit"))).status_code, 403)
