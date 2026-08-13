from django.test import TestCase

from apps.accounts.forms import UserLocationAssignmentAdminForm
from django.urls import reverse

from apps.accounts.models import Role, User, UserRoleAssignment
from apps.locations.models import Province, Tikina, Village


class LocationAssignmentAdminFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="scoped")
        self.province = Province.objects.create(code="LAU", name_en="Lau")
        self.tikina = Tikina.objects.create(province=self.province, code="LAK", name_en="Lakeba")
        self.village = Village.objects.create(tikina=self.tikina, code="TUB", name_en="Tubou")

    def test_selected_scope_clears_other_hierarchy_values(self):
        form = UserLocationAssignmentAdminForm(data={"user": self.user.pk, "location_level": "village", "province": self.province.pk, "tikina": self.tikina.pk, "village": self.village.pk, "is_active": True})
        self.assertTrue(form.is_valid(), form.errors)
        assignment = form.save()
        self.assertIsNone(assignment.province)
        self.assertIsNone(assignment.tikina)
        self.assertEqual(assignment.village, self.village)

    def test_matching_location_is_required(self):
        form = UserLocationAssignmentAdminForm(data={"user": self.user.pk, "location_level": "tikina", "province": self.province.pk, "is_active": True})
        self.assertFalse(form.is_valid())
        self.assertIn("tikina", form.errors)

    def test_role_assignment_admin_shows_user_name_and_role(self):
        self.user.first_name = "Laisa"
        self.user.last_name = "Naivalu"
        self.user.save(update_fields=("first_name", "last_name"))
        role = Role.objects.create(code=Role.Codes.TURAGA_NI_KORO, name="Turaga ni Koro")
        assignment = UserRoleAssignment.objects.create(user=self.user, role=role)
        self.assertEqual(str(assignment), "Laisa Naivalu — Turaga ni Koro")

        administrator = User.objects.create_superuser(username="admin", password="safe-password", email="admin@example.test")
        self.client.force_login(administrator)
        response = self.client.get(reverse("admin:accounts_userroleassignment_changelist"))
        self.assertContains(response, "Laisa Naivalu")
        self.assertContains(response, "Turaga ni Koro")
        self.assertNotContains(response, "UserRoleAssignment object")
