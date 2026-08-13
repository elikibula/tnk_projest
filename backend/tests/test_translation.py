from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User


class LanguageSwitcherTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="translator", password="safe-password")
        self.client.force_login(self.user)

    def test_switch_to_itaukei_changes_rendered_interface_and_selection(self):
        response = self.client.post(reverse("set_language"), {"language": "fj", "next": reverse("core:dashboard")}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<html lang="fj">', html=False)
        self.assertContains(response, "Ripote")
        self.assertContains(response, "Vakadikevi ni itukutuku")
        self.assertContains(response, '<option value="fj" selected>iTaukei</option>', html=False)

    def test_switch_back_to_english(self):
        self.client.post(reverse("set_language"), {"language": "fj", "next": "/"})
        response = self.client.post(reverse("set_language"), {"language": "en", "next": "/"}, follow=True)
        self.assertContains(response, '<html lang="en">', html=False)
        self.assertContains(response, "Reports")
        self.assertContains(response, '<option value="en" selected>English</option>', html=False)
