import json
import logging
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.test import TestCase
from django.urls import reverse

from apps.core.logging import JsonFormatter
from apps.core.management.commands.staging_rehearsal import Command as StagingRehearsalCommand
from apps.reporting.models import TNKReport


class PhaseHReadinessTests(TestCase):
    def test_healthcheck_is_database_aware_and_has_security_headers(self):
        response = self.client.get(reverse("healthcheck"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        self.assertIn("default-src 'self'", response.headers["Content-Security-Policy"])
        self.assertIn("camera=()", response.headers["Permissions-Policy"])
        self.assertEqual(len(response.headers["X-Request-ID"]), 32)

    def test_templates_use_local_tailwind_without_inline_language_script(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, "/static/css/tailwind.css")
        self.assertContains(response, "/static/js/app.js")
        self.assertNotContains(response, "cdn.tailwindcss.com")
        self.assertNotContains(response, "onchange=")

    def test_structured_logger_ignores_sensitive_extra_fields(self):
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JsonFormatter())
        logger = logging.getLogger("phase_h_test")
        logger.handlers = [handler]
        logger.propagate = False
        logger.setLevel(logging.INFO)
        logger.info("Safe event", extra={"event": "test", "password": "secret", "token": "secret-token"})
        payload = json.loads(stream.getvalue())
        self.assertEqual(payload["event"], "test")
        self.assertNotIn("password", payload)
        self.assertNotIn("token", payload)
        self.assertNotIn("secret", stream.getvalue())

    def test_rehearsal_command_refuses_non_postgresql_database(self):
        with (
            patch.object(connection, "vendor", "sqlite"),
            self.assertRaisesMessage(CommandError, "requires PostgreSQL"),
        ):
            call_command("staging_rehearsal")

    def test_rehearsal_seeds_reference_data_without_development_demo_data(self):
        command = StagingRehearsalCommand()
        with (
            patch(
                "apps.core.management.commands.staging_rehearsal.call_command"
            ) as mocked_call,
            patch.object(TNKReport.objects, "exists", return_value=False),
            patch(
                "apps.core.management.commands.staging_rehearsal.Province.objects.create",
                side_effect=RuntimeError("stop after approved reference seeding"),
            ),
            self.assertRaisesMessage(RuntimeError, "stop after approved reference seeding"),
        ):
            command._run()

        mocked_call.assert_called_once_with("seed_reference_data", verbosity=0)
