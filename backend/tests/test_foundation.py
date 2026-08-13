from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from apps.accounts.models import User, UserLocationAssignment
from apps.accounts.selectors import villages_for_user
from apps.locations.models import Province, Tikina, Village

class FoundationTests(TestCase):
    def setUp(self):
        self.province = Province.objects.create(code="LAU", name_en="Lau")
        self.tikina = Tikina.objects.create(province=self.province, code="LAKEBA", name_en="Lakeba")
        self.village = Village.objects.create(tikina=self.tikina, code="TUBOU", name_en="Tubou")

    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse("core:dashboard"))
        self.assertRedirects(response, f"{reverse('login')}?next=/")

    def test_authenticated_dashboard_renders_responsive_user_navigation(self):
        user = User.objects.create_user(username="friendly-user", password="safe-password")
        UserLocationAssignment.objects.create(user=user, village=self.village)
        self.client.force_login(user)
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="app-sidebar"', html=False)
        self.assertContains(response, 'class="mobile-header"', html=False)
        self.assertContains(response, "Quick guide")
        self.assertContains(response, "Reports in scope")

    def test_login_page_uses_accessible_friendly_layout(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, 'class="login-card"', html=False)
        self.assertContains(response, 'autocomplete="username"', html=False)
        self.assertContains(response, "Welcome back")

    def test_village_assignment_limits_queryset(self):
        other = Village.objects.create(tikina=self.tikina, code="LEVUKA", name_en="Levuka")
        user = User.objects.create_user(username="tnk", password="safe-password")
        UserLocationAssignment.objects.create(user=user, village=self.village)
        self.assertQuerySetEqual(villages_for_user(user), [self.village])
        self.assertNotIn(other, villages_for_user(user))

    def test_location_assignment_requires_exactly_one_level(self):
        assignment = UserLocationAssignment(user=User.objects.create_user(username="bad"), province=self.province, village=self.village)
        with self.assertRaises(ValidationError):
            assignment.full_clean()

    def test_location_codes_are_scoped_to_parent(self):
        other_province = Province.objects.create(code="KAD", name_en="Kadavu")
        Tikina.objects.create(province=other_province, code="LAKEBA", name_en="Another Lakeba")
        self.assertEqual(self.province.tikina.count(), 1)
