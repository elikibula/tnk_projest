from datetime import date

from django.contrib.admin.sites import AdminSite
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import RequestFactory, TestCase
from django.urls import reverse

from apps.accounts.models import Role, User, UserLocationAssignment, UserRoleAssignment
from apps.audit.models import AuditEvent
from apps.locations.models import Province, Tikina, Village
from apps.reporting.admin import TNKReportAdmin
from apps.reporting.models import ReportSectionStatus, ReportingPeriod, TNKReport
from apps.reporting.services import create_report
from apps.workflow.models import FinalDeclaration
from apps.workflow.services import TRANSITIONS, available_actions, transition_report


class AuthoritativeWorkflowTests(TestCase):
    def setUp(self):
        self.province = Province.objects.create(code="TEST", name_en="Test Province")
        self.tikina = Tikina.objects.create(province=self.province, code="A", name_en="Tikina A")
        self.other_tikina = Tikina.objects.create(province=self.province, code="B", name_en="Tikina B")
        self.village = Village.objects.create(tikina=self.tikina, code="A1", name_en="Village A1")
        self.other_village = Village.objects.create(tikina=self.other_tikina, code="B1", name_en="Village B1")
        self.period = ReportingPeriod.objects.create(
            year=2026,
            quarter=2,
            start_date=date(2026, 4, 1),
            end_date=date(2026, 6, 30),
            submission_due_date=date(2026, 12, 31),
            is_open=True,
        )
        self.users = {
            "system_admin": self.make_user("system-admin", Role.Codes.SYSTEM_ADMIN, province=self.province),
            "provincial_admin": self.make_user("provincial-admin", Role.Codes.PROVINCIAL_ADMIN, province=self.province),
            "roko_tui": self.make_user("roko-tui", Role.Codes.ROKO_TUI, province=self.province),
            "roko_veivuke": self.make_user("roko-veivuke", Role.Codes.ROKO_VEIVUKE, tikina=self.tikina),
            "mata": self.make_user("mata", Role.Codes.MATA_NI_TIKINA, tikina=self.tikina),
            "tnk": self.make_user("tnk", Role.Codes.TURAGA_NI_KORO, village=self.village),
            "assistant": self.make_user("assistant", Role.Codes.VILLAGE_DATA_ASSISTANT, village=self.village),
            "nurse": self.make_user("nurse", Role.Codes.VILLAGE_NURSE, village=self.village),
            "analyst": self.make_user("analyst", Role.Codes.READ_ONLY_ANALYST, province=self.province),
            "auditor": self.make_user("auditor", Role.Codes.AUDITOR, province=self.province),
        }
        self.outsider = self.make_user("outside-mata", Role.Codes.MATA_NI_TIKINA, tikina=self.other_tikina)
        self.report = create_report(village=self.village, reporting_period=self.period, prepared_by=self.users["tnk"])
        self.complete_and_declare()

    def make_user(self, username, role_code, **location):
        user = User.objects.create_user(username=username)
        role, _ = Role.objects.get_or_create(
            code=role_code,
            defaults={"name": Role(code=role_code).get_code_display()},
        )
        UserRoleAssignment.objects.create(user=user, role=role)
        UserLocationAssignment.objects.create(user=user, **location)
        return user

    def complete_and_declare(self):
        self.report.section_statuses.update(
            status=ReportSectionStatus.Status.COMPLETE,
            completion_percentage=100,
        )
        FinalDeclaration.objects.update_or_create(
            report=self.report,
            defaults={
                "declared_by": self.users["tnk"],
                "declaration_text": "Complete and accurate",
                "acknowledged": True,
            },
        )

    def force_status(self, status):
        TNKReport.objects.filter(pk=self.report.pk).update(status=status)
        self.report.refresh_from_db()

    def transition_kwargs(self, action):
        return {
            "comment": "Required reason" if action in {"return", "reject", "archive"} else "",
            "acknowledged": action in {"approve", "lock", "archive"},
        }

    def test_every_allowed_role_and_source_transition(self):
        cases = (
            ("mark_ready", TNKReport.Status.DRAFT, ("tnk", "assistant")),
            ("mark_ready", TNKReport.Status.RETURNED_TO_VILLAGE, ("tnk", "assistant")),
            ("reopen_draft", TNKReport.Status.READY_FOR_VALIDATION, ("tnk", "assistant")),
            ("submit", TNKReport.Status.READY_FOR_VALIDATION, ("tnk",)),
            ("start_tikina_review", TNKReport.Status.SUBMITTED, ("mata", "roko_veivuke")),
            ("return", TNKReport.Status.SUBMITTED, ("mata", "roko_veivuke")),
            ("return", TNKReport.Status.UNDER_TIKINA_REVIEW, ("mata", "roko_veivuke")),
            ("return", TNKReport.Status.UNDER_PROVINCIAL_REVIEW, ("roko_tui",)),
            ("forward", TNKReport.Status.UNDER_TIKINA_REVIEW, ("mata", "roko_veivuke")),
            ("reject", TNKReport.Status.UNDER_TIKINA_REVIEW, ("mata", "roko_veivuke")),
            ("reject", TNKReport.Status.UNDER_PROVINCIAL_REVIEW, ("roko_tui",)),
            ("approve", TNKReport.Status.UNDER_PROVINCIAL_REVIEW, ("roko_tui",)),
            ("lock", TNKReport.Status.APPROVED, ("roko_tui", "system_admin")),
            ("archive", TNKReport.Status.LOCKED, ("roko_tui", "system_admin")),
        )
        for action, source, user_names in cases:
            for user_name in user_names:
                with self.subTest(action=action, source=source, user=user_name):
                    self.force_status(source)
                    self.complete_and_declare()
                    transition = transition_report(
                        report=self.report,
                        user=self.users[user_name],
                        action=action,
                        **self.transition_kwargs(action),
                    )
                    self.report.refresh_from_db()
                    self.assertEqual(self.report.status, TRANSITIONS[action].target)
                    self.assertEqual(transition.from_status, source)
                    self.assertEqual(transition.to_status, TRANSITIONS[action].target)
                    self.assertTrue(AuditEvent.objects.filter(action=f"report.{action}", object_uuid=self.report.uuid).exists())

    def test_every_unapproved_role_is_forbidden_for_each_action(self):
        all_user_names = set(self.users)
        cases = (
            ("mark_ready", TNKReport.Status.DRAFT, {"tnk", "assistant"}),
            ("reopen_draft", TNKReport.Status.READY_FOR_VALIDATION, {"tnk", "assistant"}),
            ("submit", TNKReport.Status.READY_FOR_VALIDATION, {"tnk"}),
            ("start_tikina_review", TNKReport.Status.SUBMITTED, {"mata", "roko_veivuke"}),
            ("return", TNKReport.Status.SUBMITTED, {"mata", "roko_veivuke"}),
            ("forward", TNKReport.Status.UNDER_TIKINA_REVIEW, {"mata", "roko_veivuke"}),
            ("reject", TNKReport.Status.UNDER_TIKINA_REVIEW, {"mata", "roko_veivuke"}),
            ("approve", TNKReport.Status.UNDER_PROVINCIAL_REVIEW, {"roko_tui"}),
            ("lock", TNKReport.Status.APPROVED, {"roko_tui", "system_admin"}),
            ("archive", TNKReport.Status.LOCKED, {"roko_tui", "system_admin"}),
        )
        for action, source, allowed in cases:
            for user_name in sorted(all_user_names - allowed):
                with self.subTest(action=action, source=source, forbidden_user=user_name):
                    self.force_status(source)
                    self.complete_and_declare()
                    with self.assertRaises(PermissionDenied):
                        transition_report(
                            report=self.report,
                            user=self.users[user_name],
                            action=action,
                            **self.transition_kwargs(action),
                        )
                    self.report.refresh_from_db()
                    self.assertEqual(self.report.status, source)

    def test_wrong_state_is_forbidden_for_every_action(self):
        actor_by_action = {
            "mark_ready": "tnk",
            "reopen_draft": "tnk",
            "submit": "tnk",
            "start_tikina_review": "mata",
            "return": "mata",
            "forward": "mata",
            "reject": "mata",
            "approve": "roko_tui",
            "lock": "roko_tui",
            "archive": "roko_tui",
        }
        for action, actor in actor_by_action.items():
            with self.subTest(action=action):
                self.force_status(TNKReport.Status.ARCHIVED)
                with self.assertRaises(ValidationError):
                    transition_report(
                        report=self.report,
                        user=self.users[actor],
                        action=action,
                        **self.transition_kwargs(action),
                    )

    def test_comments_acknowledgements_declaration_and_self_approval_are_required(self):
        for action, source, actor in (
            ("return", TNKReport.Status.SUBMITTED, "mata"),
            ("reject", TNKReport.Status.UNDER_TIKINA_REVIEW, "mata"),
            ("archive", TNKReport.Status.LOCKED, "roko_tui"),
        ):
            with self.subTest(comment_action=action):
                self.force_status(source)
                with self.assertRaises(ValidationError):
                    transition_report(
                        report=self.report,
                        user=self.users[actor],
                        action=action,
                        acknowledged=action == "archive",
                    )
        for action, source in (("approve", TNKReport.Status.UNDER_PROVINCIAL_REVIEW), ("lock", TNKReport.Status.APPROVED), ("archive", TNKReport.Status.LOCKED)):
            with self.subTest(acknowledgement_action=action):
                self.force_status(source)
                with self.assertRaises(ValidationError):
                    transition_report(
                        report=self.report,
                        user=self.users["roko_tui"],
                        action=action,
                        comment="Archive reason" if action == "archive" else "",
                    )
        self.force_status(TNKReport.Status.READY_FOR_VALIDATION)
        FinalDeclaration.objects.filter(report=self.report).update(acknowledged=False)
        with self.assertRaises(ValidationError):
            transition_report(report=self.report, user=self.users["tnk"], action="submit")

        roko_role = Role.objects.get(code=Role.Codes.ROKO_TUI)
        UserRoleAssignment.objects.create(user=self.users["tnk"], role=roko_role)
        self.force_status(TNKReport.Status.UNDER_PROVINCIAL_REVIEW)
        with self.assertRaises(PermissionDenied):
            transition_report(report=self.report, user=self.users["tnk"], action="approve", acknowledged=True)

    def test_return_and_reopen_invalidate_declaration(self):
        self.force_status(TNKReport.Status.SUBMITTED)
        transition_report(report=self.report, user=self.users["mata"], action="return", comment="Correct totals")
        self.assertFalse(FinalDeclaration.objects.get(report=self.report).acknowledged)
        action = self.report.approval_actions.latest("acted_at")
        self.assertEqual(action.comment, "Correct totals")

        self.complete_and_declare()
        self.force_status(TNKReport.Status.READY_FOR_VALIDATION)
        transition_report(report=self.report, user=self.users["assistant"], action="reopen_draft")
        self.assertFalse(FinalDeclaration.objects.get(report=self.report).acknowledged)

    def test_location_scope_is_enforced_by_service_and_post(self):
        self.force_status(TNKReport.Status.SUBMITTED)
        with self.assertRaises(PermissionDenied):
            transition_report(report=self.report, user=self.outsider, action="start_tikina_review")
        self.client.force_login(self.outsider)
        response = self.client.post(reverse("reporting:workflow_action", args=(self.report.uuid, "start_tikina_review")))
        self.assertEqual(response.status_code, 404)
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, TNKReport.Status.SUBMITTED)

    def test_direct_post_complete_return_and_resubmit_flow(self):
        def post_as(user_name, action, data=None):
            self.client.force_login(self.users[user_name])
            response = self.client.post(
                reverse("reporting:workflow_action", args=(self.report.uuid, action)),
                data or {},
            )
            self.assertEqual(response.status_code, 302)
            self.report.refresh_from_db()

        post_as("tnk", "mark_ready")
        post_as("tnk", "submit")
        post_as("mata", "start_tikina_review")
        post_as("mata", "return", {"comment": "Correct the water section"})
        self.client.force_login(self.users["tnk"])
        self.client.post(reverse("reporting:declare", args=(self.report.uuid,)), {"acknowledged": "on"})
        post_as("tnk", "mark_ready")
        post_as("tnk", "submit")
        post_as("roko_veivuke", "start_tikina_review")
        post_as("roko_veivuke", "forward")
        post_as("roko_tui", "approve", {"acknowledged": "on"})
        post_as("roko_tui", "lock", {"acknowledged": "on"})
        post_as("system_admin", "archive", {"acknowledged": "on", "comment": "Retention archive"})
        self.assertEqual(self.report.status, TNKReport.Status.ARCHIVED)
        self.assertEqual(self.report.approval_actions.count(), 11)

    def test_direct_post_role_matrix_does_not_rely_on_hidden_buttons(self):
        for user_name in self.users:
            with self.subTest(user=user_name):
                self.force_status(TNKReport.Status.DRAFT)
                self.complete_and_declare()
                self.client.force_login(self.users[user_name])
                response = self.client.post(
                    reverse("reporting:workflow_action", args=(self.report.uuid, "mark_ready"))
                )
                self.assertEqual(response.status_code, 302)
                self.report.refresh_from_db()
                expected = (
                    TNKReport.Status.READY_FOR_VALIDATION
                    if user_name in {"tnk", "assistant"}
                    else TNKReport.Status.DRAFT
                )
                self.assertEqual(self.report.status, expected)

    def test_available_actions_match_role_policy(self):
        self.force_status(TNKReport.Status.DRAFT)
        self.assertEqual(available_actions(self.report, self.users["tnk"]), ["mark_ready"])
        self.assertEqual(available_actions(self.report, self.users["assistant"]), ["mark_ready"])
        for user_name in {"system_admin", "provincial_admin", "roko_tui", "roko_veivuke", "mata", "nurse", "analyst", "auditor"}:
            self.assertEqual(available_actions(self.report, self.users[user_name]), [])

    def test_status_cannot_be_changed_by_direct_save_or_admin_form(self):
        self.report.status = TNKReport.Status.APPROVED
        with self.assertRaises(ValidationError):
            self.report.save(update_fields=("status",))
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, TNKReport.Status.DRAFT)

        request = RequestFactory().get("/admin/reporting/tnkreport/")
        request.user = self.users["system_admin"]
        model_admin = TNKReportAdmin(TNKReport, AdminSite())
        self.assertIn("status", model_admin.get_readonly_fields(request, self.report))

    def test_ready_report_is_frozen_and_unsupported_actions_fail(self):
        transition_report(report=self.report, user=self.users["tnk"], action="mark_ready")
        self.report.refresh_from_db()
        self.assertFalse(self.report.is_editable)
        with self.assertRaises(ValidationError):
            transition_report(report=self.report, user=self.users["tnk"], action="invented")

    def test_period_archive_command_uses_accountable_workflow_transition(self):
        self.force_status(TNKReport.Status.LOCKED)
        with self.assertRaises(CommandError):
            call_command(
                "archive_reporting_period",
                2026,
                2,
                actor=self.users["system_admin"].username,
                reason="Retention schedule",
            )
        call_command(
            "archive_reporting_period",
            2026,
            2,
            actor=self.users["system_admin"].username,
            reason="Retention schedule",
            acknowledge=True,
            verbosity=0,
        )
        self.report.refresh_from_db()
        self.period.refresh_from_db()
        self.assertEqual(self.report.status, TNKReport.Status.ARCHIVED)
        self.assertTrue(self.period.is_locked)
        self.assertEqual(self.report.approval_actions.get(action_type="archive").comment, "Retention schedule")
