from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Role, User, UserLocationAssignment, UserRoleAssignment
from apps.audit.models import AuditEvent
from apps.locations.models import Province, Tikina, Village
from apps.reporting.models import ReportingPeriod


class FrontendAdministrationTests(TestCase):
    def setUp(self):
        self.province = Province.objects.create(code="FA-1", name_en="Frontend A")
        self.other_province = Province.objects.create(code="FA-2", name_en="Frontend B")
        self.tikina = Tikina.objects.create(province=self.province, code="FA-T1", name_en="Tikina A")
        self.other_tikina = Tikina.objects.create(province=self.other_province, code="FA-T2", name_en="Tikina B")
        self.village = Village.objects.create(tikina=self.tikina, code="FA-V1", name_en="Village A")
        self.other_village = Village.objects.create(tikina=self.other_tikina, code="FA-V2", name_en="Village B")
        self.system = self.make_user("system-front", Role.Codes.SYSTEM_ADMIN)
        self.provincial = self.make_user("province-front", Role.Codes.PROVINCIAL_ADMIN, province=self.province)
        self.normal = self.make_user("normal-front", Role.Codes.TURAGA_NI_KORO, village=self.village)
        self.target = self.make_user("target-front", Role.Codes.TURAGA_NI_KORO, village=self.village)
        self.outside = self.make_user("outside-front", Role.Codes.TURAGA_NI_KORO, village=self.other_village)

    def make_user(self, username, role_code, **location):
        user = User.objects.create_user(username=username, password="Strong-test-password-782!")
        role, _ = Role.objects.get_or_create(code=role_code, defaults={"name": Role(code=role_code).get_code_display()})
        UserRoleAssignment.objects.create(user=user, role=role)
        if location:
            UserLocationAssignment.objects.create(user=user, **location)
        return user

    def test_anonymous_and_normal_users_cannot_access_any_administration_url(self):
        urls = [reverse("administration:dashboard"), reverse("administration:user_list"), reverse("administration:period_list"), reverse("administration:location_list"), reverse("administration:audit_list")]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(self.normal)
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 403)

    def test_administrators_can_open_dashboard_and_navigation_is_role_based(self):
        for administrator in (self.provincial, self.system):
            self.client.force_login(administrator)
            response = self.client.get(reverse("administration:dashboard"))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Administration Centre")
        self.client.force_login(self.normal)
        response = self.client.get(reverse("core:dashboard"))
        self.assertNotContains(response, reverse("administration:dashboard"))

    def test_provincial_user_list_and_details_are_location_scoped(self):
        self.client.force_login(self.provincial)
        response = self.client.get(reverse("administration:user_list"))
        self.assertContains(response, self.target.username)
        self.assertNotContains(response, self.outside.username)
        self.assertEqual(self.client.get(reverse("administration:user_detail", args=(self.outside.uuid,))).status_code, 404)

    def test_provincial_admin_creates_hashed_village_user_but_cannot_escalate(self):
        village_role = Role.objects.get(code=Role.Codes.TURAGA_NI_KORO)
        self.client.force_login(self.provincial)
        response = self.client.post(reverse("administration:user_create"), {
            "first_name": "Created", "last_name": "User", "username": "created-front", "email": "created@example.test",
            "preferred_language": "en", "is_active": "on", "role": village_role.pk, "village": self.village.pk,
            "password1": "Secure-created-password-917!", "password2": "Secure-created-password-917!",
        })
        self.assertEqual(response.status_code, 302)
        created = User.objects.get(username="created-front")
        self.assertTrue(created.check_password("Secure-created-password-917!"))
        self.assertNotEqual(created.password, "Secure-created-password-917!")
        self.assertEqual(created.location_assignments.get(is_active=True).village, self.village)
        self.assertTrue(AuditEvent.objects.filter(action="user.created", object_uuid=created.uuid).exists())

        system_role = Role.objects.get(code=Role.Codes.SYSTEM_ADMIN)
        denied = self.client.post(reverse("administration:user_create"), {
            "username": "escalated-front", "preferred_language": "en", "is_active": "on", "role": system_role.pk,
            "password1": "Secure-created-password-917!", "password2": "Secure-created-password-917!",
        })
        self.assertEqual(denied.status_code, 200)
        self.assertFalse(User.objects.filter(username="escalated-front").exists())

    def test_role_location_rules_and_out_of_scope_locations_are_rejected(self):
        village_role = Role.objects.get(code=Role.Codes.TURAGA_NI_KORO)
        self.client.force_login(self.provincial)
        base = {"username": "invalid-front", "preferred_language": "en", "is_active": "on", "role": village_role.pk, "password1": "Secure-created-password-917!", "password2": "Secure-created-password-917!"}
        response = self.client.post(reverse("administration:user_create"), base)
        self.assertContains(response, "requires a village assignment")
        response = self.client.post(reverse("administration:user_create"), {**base, "village": self.other_village.pk})
        self.assertContains(response, "Select a valid choice")

    def test_sensitive_user_status_change_requires_post_and_is_audited(self):
        self.client.force_login(self.provincial)
        url = reverse("administration:user_toggle_active", args=(self.target.uuid,))
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertEqual(self.client.post(url).status_code, 302)
        self.target.refresh_from_db()
        self.assertFalse(self.target.is_active)
        self.assertTrue(AuditEvent.objects.filter(action="user.deactivated", object_uuid=self.target.uuid).exists())

    def test_last_system_administrator_cannot_be_deactivated_or_demoted(self):
        self.client.force_login(self.system)
        toggle = reverse("administration:user_toggle_active", args=(self.system.uuid,))
        self.assertEqual(self.client.post(toggle).status_code, 403)
        self.system.refresh_from_db()
        self.assertTrue(self.system.is_active)
        ordinary_role = Role.objects.get(code=Role.Codes.TURAGA_NI_KORO)
        response = self.client.post(reverse("administration:user_edit", args=(self.system.uuid,)), {
            "username": self.system.username, "preferred_language": "en", "is_active": "on",
            "role": ordinary_role.pk, "village": self.village.pk,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "last active System Administrator cannot be demoted")

    def test_only_system_admin_mutates_reporting_periods_and_validation_prevents_duplicates(self):
        self.client.force_login(self.provincial)
        self.assertEqual(self.client.get(reverse("administration:period_create")).status_code, 403)
        self.client.force_login(self.system)
        payload = {"year": 2026, "quarter": 3, "start_date": "2026-07-01", "end_date": "2026-09-30", "submission_due_date": "2026-10-15"}
        self.assertEqual(self.client.post(reverse("administration:period_create"), payload).status_code, 302)
        self.assertEqual(ReportingPeriod.objects.count(), 1)
        duplicate = self.client.post(reverse("administration:period_create"), payload)
        self.assertEqual(duplicate.status_code, 200)
        self.assertEqual(ReportingPeriod.objects.count(), 1)
        invalid = self.client.post(reverse("administration:period_create"), {**payload, "quarter": 4, "start_date": "2026-12-31", "end_date": "2026-10-01"})
        self.assertContains(invalid, "Start date must be before end date")
        period = ReportingPeriod.objects.get()
        edit = self.client.post(reverse("administration:period_edit", args=(period.uuid,)), {**payload, "submission_due_date": "2026-10-20"})
        self.assertEqual(edit.status_code, 302)
        self.assertTrue(AuditEvent.objects.filter(action="reporting_period.updated", object_uuid=period.uuid).exists())

    def test_location_management_is_scoped_and_provincial_admin_cannot_edit_province(self):
        self.client.force_login(self.provincial)
        response = self.client.get(reverse("administration:location_list") + "?type=village")
        self.assertContains(response, self.village.name_en)
        self.assertNotContains(response, self.other_village.name_en)
        self.assertEqual(self.client.get(reverse("administration:location_edit", args=("province", self.province.uuid))).status_code, 403)
        created = self.client.post(reverse("administration:location_create", args=("village",)), {"tikina": self.tikina.pk, "code": "FA-V3", "name_en": "Village New", "is_active": "on"})
        self.assertEqual(created.status_code, 302)
        self.assertTrue(Village.objects.filter(code="FA-V3").exists())

    def test_provincial_audit_log_excludes_other_province_and_unscoped_events(self):
        AuditEvent.objects.create(actor=self.system, action="local.a", object_type="locations.Village", object_uuid=self.village.uuid, summary="Visible", village=self.village, tikina=self.tikina, province=self.province)
        AuditEvent.objects.create(actor=self.system, action="local.b", object_type="locations.Village", object_uuid=self.other_village.uuid, summary="Hidden", village=self.other_village, tikina=self.other_tikina, province=self.other_province)
        AuditEvent.objects.create(actor=self.system, action="central", object_type="system", summary="Central hidden")
        self.client.force_login(self.provincial)
        response = self.client.get(reverse("administration:audit_list"))
        self.assertContains(response, "Visible")
        self.assertNotContains(response, "Hidden")
        self.assertNotContains(response, "Central hidden")
