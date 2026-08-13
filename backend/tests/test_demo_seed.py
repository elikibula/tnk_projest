from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase, override_settings

from apps.accounts.models import User
from apps.analytics.models import IndicatorValue
from apps.documents.models import EvidenceDocument
from apps.reporting.models import TNKReport
from apps.reporting.section_entries import entry_queryset
from apps.reporting.section_registry import SECTION_ENTRIES


@override_settings(DEBUG=True, MEDIA_ROOT=Path(__file__).resolve().parents[1] / "test_media")
class DemoSeedTests(TestCase):
    def test_complete_demo_seed_is_repeatable_and_populates_all_entry_types(self):
        output = StringIO()
        call_command("seed_demo_data", stdout=output)

        reports = TNKReport.objects.filter(
            village__tikina__province__code="DEMO", reporting_period__year=2099
        )
        self.assertEqual(reports.count(), 4)
        self.assertSetEqual(
            set(reports.values_list("status", flat=True)),
            {"draft", "submitted", "under_tikina_review", "approved"},
        )
        self.assertEqual(User.objects.filter(username__startswith="demo_").count(), 14)
        self.assertTrue(User.objects.get(username="demo_admin").check_password("Demo-TNK-2026!"))
        self.assertTrue(IndicatorValue.objects.filter(reporting_period__year=2099).exists())

        current = reports.get(village__code="DEMO-A1", reporting_period__quarter=2)
        for section_code, configs in SECTION_ENTRIES.items():
            for config in configs:
                self.assertTrue(
                    entry_queryset(config, current).exists(),
                    f"Missing demo row for {section_code}/{config.key}",
                )

        for document in EvidenceDocument.objects.filter(title__startswith="Fictional minutes"):
            self.addCleanup(document.file.storage.delete, document.file.name)

        first_document_count = EvidenceDocument.objects.count()
        call_command("seed_demo_data", stdout=output)
        self.assertEqual(reports.count(), 4)
        self.assertEqual(EvidenceDocument.objects.count(), first_document_count)
        self.assertIn("already installed", output.getvalue())
