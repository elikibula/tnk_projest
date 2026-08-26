from io import StringIO
from pathlib import Path
import tempfile
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from apps.accounts.models import User, UserLocationAssignment
from apps.analytics.models import IndicatorValue
from apps.documents.models import EvidenceDocument, RecordPhoto
from apps.reporting.models import ReportingPeriod, TNKReport
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

    def test_showcase_populates_twelve_reports_photos_analytics_and_preserves_existing(self):
        with tempfile.TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=Path(directory) / "media"):
            call_command("seed_demo_data", stdout=StringIO())
            originals = list(TNKReport.objects.order_by("pk").values())
            accounts = list(User.objects.order_by("pk").values())
            assignments = list(UserLocationAssignment.objects.order_by("pk").values())
            image_dir = Path(directory) / "images"
            image_dir.mkdir()
            for name in ("farm", "water", "housing", "project", "climate"):
                Image.new("RGB", (40, 30), "green").save(image_dir / f"{name}.png")
            # Fail after the first report's files were saved: SQL and new files must roll back.
            from apps.core.management.commands.seed_demo_showcase import Command
            with patch.object(Command, "_workflow", side_effect=RuntimeError("test rollback")):
                with self.assertRaisesMessage(RuntimeError, "test rollback"):
                    call_command("seed_demo_showcase", image_dir=image_dir, stdout=StringIO())
            self.assertFalse(TNKReport.objects.filter(reporting_period__year=2100).exists())
            self.assertFalse(list((Path(directory) / "media").rglob("*.png")))

            call_command("seed_demo_showcase", image_dir=image_dir, stdout=StringIO())
            reports = TNKReport.objects.filter(reporting_period__year=2100)
            self.assertEqual(reports.count(), 12)
            self.assertEqual(reports.filter(status="approved").count(), 8)
            self.assertEqual(reports.filter(status="draft").count(), 1)
            self.assertEqual(RecordPhoto.objects.count(), 60)
            for report in reports:
                self.assertEqual(report.record_photos.count(), 5)
                for section, configs in SECTION_ENTRIES.items():
                    for config in configs:
                        self.assertTrue(entry_queryset(config, report).exists(), f"{report}: {section}/{config.key}")
            self.assertTrue(IndicatorValue.objects.filter(reporting_period__year=2100, indicator__code="total_population", value__gt=0).exists())
            self.assertGreater(IndicatorValue.objects.filter(reporting_period__year=2100, village__isnull=False, indicator__code="total_population").values("value").distinct().count(), 1)
            self.assertEqual(list(TNKReport.objects.filter(pk__in=[row["id"] for row in originals]).order_by("pk").values()), originals)
            self.assertEqual(list(User.objects.order_by("pk").values()), accounts)
            self.assertEqual(list(UserLocationAssignment.objects.order_by("pk").values()), assignments)

            self.client.force_login(User.objects.get(username="demo_roko_veivuke"))
            approved = reports.filter(status="approved").first()
            gallery = self.client.get(reverse("reporting:photo_report_detail", args=[approved.uuid]))
            self.assertEqual(gallery.status_code, 200)
            self.assertEqual(gallery.context["total_photos"], 5)
            photo = approved.record_photos.first()
            preview = self.client.get(reverse("documents:photo_preview", args=[photo.document.uuid]))
            self.assertEqual(preview.status_code, 200)
            self.assertEqual(preview["Content-Type"], "image/jpeg")
            response = self.client.get(reverse("analytics:dashboard"), {"period": ReportingPeriod.objects.get(year=2100, quarter=2).pk})
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["summary"]["indicators"]["population"]["has_data"])
            self.client.force_login(User.objects.get(username="demo_tnk_b1"))
            self.assertEqual(self.client.get(reverse("reporting:photo_report_detail", args=[approved.uuid])).status_code, 403)

            snapshot = list(reports.order_by("pk").values())
            files_before = sorted(str(path) for path in (Path(directory) / "media").rglob("*"))
            call_command("seed_demo_showcase", image_dir=image_dir, stdout=StringIO())
            self.assertEqual(list(reports.order_by("pk").values()), snapshot)
            self.assertEqual(RecordPhoto.objects.count(), 60)
            self.assertEqual(sorted(str(path) for path in (Path(directory) / "media").rglob("*")), files_before)

    @override_settings(DEBUG=False)
    def test_showcase_refuses_production(self):
        with self.assertRaisesMessage(CommandError, "DEBUG=True"):
            call_command("seed_demo_showcase")

    def test_showcase_refuses_to_create_or_reset_missing_demo_accounts(self):
        with self.assertRaisesMessage(CommandError, "Existing demo accounts"):
            call_command("seed_demo_showcase")
        self.assertFalse(User.objects.exists())
        self.assertFalse(ReportingPeriod.objects.exists())
