from datetime import date

from django.contrib import admin
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase
from django.urls import reverse

from apps.accounts.models import Role, User, UserLocationAssignment, UserRoleAssignment
from apps.audit.models import AuditEvent
from apps.audit.services import record_event
from apps.locations.models import Province, Tikina, Village
from apps.population.models import Household, PopulationMovement
from apps.reporting.models import ReportingPeriod
from apps.reporting.services import create_report


class AdminAuditControlTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.province_a = Province.objects.create(code="ADM-A", name_en="Admin Province A")
        self.province_b = Province.objects.create(code="ADM-B", name_en="Admin Province B")
        self.tikina_a = Tikina.objects.create(province=self.province_a, code="ADM-TA", name_en="Admin Tikina A")
        self.tikina_b = Tikina.objects.create(province=self.province_b, code="ADM-TB", name_en="Admin Tikina B")
        self.village_a = Village.objects.create(tikina=self.tikina_a, code="ADM-VA", name_en="Admin Village A")
        self.village_b = Village.objects.create(tikina=self.tikina_b, code="ADM-VB", name_en="Admin Village B")
        self.system = self.make_staff("system", Role.Codes.SYSTEM_ADMIN)
        self.provincial = self.make_staff("provincial", Role.Codes.PROVINCIAL_ADMIN, province=self.province_a)
        self.auditor = self.make_staff("auditor", Role.Codes.AUDITOR, province=self.province_a)
        self.untrusted = self.make_staff("ordinary-staff", Role.Codes.TURAGA_NI_KORO, province=self.province_a)
        for user in (self.system, self.provincial, self.auditor, self.untrusted):
            user.user_permissions.set(Permission.objects.all())
        self.target_a = User.objects.create_user(username="target-a")
        self.target_b = User.objects.create_user(username="target-b")
        UserLocationAssignment.objects.create(user=self.target_a, village=self.village_a)
        UserLocationAssignment.objects.create(user=self.target_b, village=self.village_b)
        self.household_a = Household.objects.create(
            household_code="A-1",
            village=self.village_a,
            household_head_name="Sensitive A",
            household_size=4,
            effective_from=date(2026, 1, 1),
        )
        self.household_b = Household.objects.create(
            household_code="B-1",
            village=self.village_b,
            household_head_name="Sensitive B",
            household_size=5,
            effective_from=date(2026, 1, 1),
        )
        self.period = ReportingPeriod.objects.create(
            year=2026,
            quarter=4,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 12, 31),
            submission_due_date=date(2027, 1, 15),
            is_open=True,
        )

    def make_staff(self, username, role_code, **location):
        user = User.objects.create_user(username=username, is_staff=True)
        role, _ = Role.objects.get_or_create(code=role_code, defaults={"name": Role(code=role_code).get_code_display()})
        UserRoleAssignment.objects.create(user=user, role=role)
        if location:
            UserLocationAssignment.objects.create(user=user, **location)
        return user

    def request(self, user, path="/admin/", method="get"):
        request = getattr(self.factory, method)(path)
        request.user = user
        request.META["REMOTE_ADDR"] = "192.0.2.44"
        request.META["HTTP_USER_AGENT"] = "Phase-G-Test-Agent"
        return request

    def test_staff_status_and_global_model_permissions_do_not_bypass_admin_roles(self):
        model_admin = admin.site._registry[Household]
        request = self.request(self.untrusted)
        self.assertFalse(model_admin.has_module_permission(request))
        self.assertFalse(model_admin.has_view_permission(request, self.household_a))
        self.assertFalse(model_admin.get_queryset(request).exists())

    def test_provincial_admin_queryset_and_related_choices_are_location_scoped(self):
        household_admin = admin.site._registry[Household]
        request = self.request(self.provincial)
        self.assertEqual(list(household_admin.get_queryset(request)), [self.household_a])
        province_admin = admin.site._registry[Province]
        self.assertEqual(list(province_admin.get_queryset(request)), [self.province_a])
        movement_admin = admin.site._registry[PopulationMovement]
        village_field = PopulationMovement._meta.get_field("village")
        formfield = movement_admin.formfield_for_foreignkey(village_field, request)
        self.assertEqual(list(formfield.queryset), [self.village_a])

    def test_national_admin_sees_all_locations_while_report_admin_is_read_only(self):
        household_admin = admin.site._registry[Household]
        request = self.request(self.system)
        self.assertEqual(set(household_admin.get_queryset(request)), {self.household_a, self.household_b})
        report = create_report(village=self.village_a, reporting_period=self.period, prepared_by=self.untrusted)
        report_admin = admin.site._registry[type(report)]
        self.assertFalse(report_admin.has_add_permission(request))
        self.assertFalse(report_admin.has_change_permission(request, report))
        self.assertFalse(report_admin.has_delete_permission(request, report))

    def test_admin_usability_does_not_expose_household_head_in_list_or_search(self):
        model_admin = admin.site._registry[Household]
        request = self.request(self.provincial)
        self.assertNotIn("household_head_name", model_admin.get_list_display(request))
        self.assertNotIn("household_head_name", model_admin.get_search_fields(request))
        self.assertIn("village", model_admin.get_list_display(request))
        self.assertEqual(model_admin.date_hierarchy, "created_at")
        self.assertLessEqual(model_admin.list_per_page, 50)

    def test_location_assignment_admin_records_actor_before_after_ip_and_user_agent(self):
        assignment_admin = admin.site._registry[UserLocationAssignment]
        request = self.request(self.provincial, method="post")
        assignment = UserLocationAssignment(user=self.target_a, tikina=self.tikina_a, is_active=True)
        assignment_admin.save_model(request, assignment, form=None, change=False)
        events = AuditEvent.objects.filter(object_uuid=assignment.uuid, action="location_assignment.created")
        self.assertEqual(events.count(), 1)
        event = events.get()
        self.assertEqual(event.actor, self.provincial)
        self.assertIsNone(event.metadata["previous"])
        self.assertEqual(event.metadata["new"]["tikina_id"], self.tikina_a.pk)
        self.assertEqual(event.metadata["ip_address"], "192.0.2.44")
        self.assertEqual(event.metadata["user_agent"], "Phase-G-Test-Agent")
        self.assertEqual(event.province, self.province_a)
        self.assertEqual(event.tikina, self.tikina_a)

        assignment.is_active = False
        assignment_admin.save_model(request, assignment, form=None, change=True)
        changed = AuditEvent.objects.get(object_uuid=assignment.uuid, action="location_assignment.changed")
        self.assertTrue(changed.metadata["previous"]["is_active"])
        self.assertFalse(changed.metadata["new"]["is_active"])

    def test_provincial_role_assignment_cannot_grant_administrator_roles(self):
        assignment_admin = admin.site._registry[UserRoleAssignment]
        request = self.request(self.provincial)
        role_field = UserRoleAssignment._meta.get_field("role")
        formfield = assignment_admin.formfield_for_foreignkey(role_field, request)
        self.assertFalse(formfield.queryset.filter(code=Role.Codes.SYSTEM_ADMIN).exists())
        self.assertFalse(formfield.queryset.filter(code=Role.Codes.PROVINCIAL_ADMIN).exists())
        self.assertTrue(formfield.queryset.filter(code=Role.Codes.TURAGA_NI_KORO).exists())

        user_field = UserRoleAssignment._meta.get_field("user")
        user_formfield = assignment_admin.formfield_for_foreignkey(user_field, request)
        self.assertNotIn(self.system, user_formfield.queryset)
        self.assertNotIn(self.provincial, user_formfield.queryset)
        self.assertIn(self.target_a, user_formfield.queryset)

        user_admin = admin.site._registry[User]
        self.assertFalse(user_admin.has_add_permission(request))
        self.assertFalse(user_admin.has_change_permission(request, self.system))
        self.assertFalse(user_admin.has_change_permission(request, self.provincial))

    def test_admin_urls_enforce_role_and_location_scope(self):
        changelist_url = reverse("admin:population_household_changelist")
        self.client.force_login(self.untrusted)
        self.assertEqual(self.client.get(changelist_url).status_code, 403)

        self.client.force_login(self.provincial)
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["cl"].queryset), [self.household_a])
        allowed_url = reverse("admin:population_household_change", args=(self.household_a.pk,))
        denied_url = reverse("admin:population_household_change", args=(self.household_b.pk,))
        self.assertEqual(self.client.get(allowed_url).status_code, 200)
        self.assertNotEqual(self.client.get(denied_url).status_code, 200)

    def test_audit_events_are_location_scoped_and_immutable(self):
        movement_a = PopulationMovement.objects.create(
            village=self.village_a,
            reporting_period=self.period,
            movement_type="birth",
            movement_date=date(2026, 10, 2),
            count=1,
            data_source="village_register",
        )
        movement_b = PopulationMovement.objects.create(
            village=self.village_b,
            reporting_period=self.period,
            movement_type="birth",
            movement_date=date(2026, 10, 2),
            count=1,
            data_source="village_register",
        )
        event_a = record_event(actor=self.provincial, action="test.a", instance=movement_a, summary="Village A event")
        event_b = record_event(actor=self.system, action="test.b", instance=movement_b, summary="Village B event")
        central = AuditEvent.objects.create(action="test.central", object_type="test.Central", summary="Central event")
        audit_admin = admin.site._registry[AuditEvent]
        provincial_events = audit_admin.get_queryset(self.request(self.provincial))
        self.assertIn(event_a, provincial_events)
        self.assertNotIn(event_b, provincial_events)
        self.assertNotIn(central, provincial_events)
        auditor_events = audit_admin.get_queryset(self.request(self.auditor))
        self.assertIn(event_a, auditor_events)
        self.assertNotIn(event_b, auditor_events)
        self.assertEqual(event_a.village, self.village_a)

        event_a.summary = "Tampered"
        with self.assertRaisesMessage(ValidationError, "immutable"):
            event_a.save()
        with self.assertRaisesMessage(ValidationError, "immutable"):
            AuditEvent.objects.filter(pk=event_a.pk).update(summary="Tampered")
        with self.assertRaisesMessage(ValidationError, "immutable"):
            event_a.delete()
