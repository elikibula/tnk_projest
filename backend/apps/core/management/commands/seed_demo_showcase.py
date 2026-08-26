"""Add a complete fictional year without resetting accounts or existing reports."""
from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from PIL import Image

from apps.accounts.models import User
from apps.documents.models import RecordPhoto
from apps.documents.photos import save_record_photos
from apps.economy.models import CropProductionSnapshot, FoodSecuritySnapshot
from apps.infrastructure.models import WaterInterruption
from apps.locations.models import Village
from apps.reporting.models import ReportingPeriod, TNKReport
from apps.reporting.progress import recalculate_report_progress
from apps.reporting.section_entries import entry_queryset
from apps.reporting.section_registry import get_entry_config
from apps.reporting.services import create_report
from apps.wellbeing.models import HealthConditionSnapshot
from apps.workflow.services import transition_report

from .seed_demo_data import Command as OriginalDemoCommand


SHOWCASE_YEAR = 2100
PHOTO_TARGETS = (
    ("agriculture_food", "crop", "farm", "Fictional dalo garden"),
    ("water", "maintenance", "water", "Fictional communal water storage"),
    ("housing_assets", "housing", "housing", "Fictional building repairs"),
    ("ivdp_projects", "progress", "project", "Fictional development works illustration"),
    ("climate_disaster", "climate", "climate", "Fictional storm impact"),
)
VILLAGES = (("DEMO-A1", "tnk_a1", "mata_a"), ("DEMO-A2", "tnk_a2", "mata_a"), ("DEMO-B1", "tnk_b1", "mata_b"))
USERNAMES = {key: "demo_" + key for key in ("tnk_a1", "tnk_a2", "tnk_b1", "mata_a", "mata_b")}
USERNAMES["roko"] = "demo_roko_tui"


class Command(BaseCommand):
    help = "Add 12 complete fictional 2100 demo reports and 60 labelled synthetic photos; DEBUG only."

    def add_arguments(self, parser):
        parser.add_argument("--image-dir", type=Path, default=settings.BASE_DIR / "data" / "demo_photos")

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Demo showcase requires DEBUG=True; never enable DEBUG to seed production.")
        users = {key: User.objects.filter(username=name, is_active=True).first() for key, name in USERNAMES.items()}
        if not all(users.values()):
            raise CommandError("Existing demo accounts are required. Install seed_demo_data in a fresh development database first.")
        villages = []
        for code, _, _ in VILLAGES:
            matches = Village.objects.filter(code=code, tikina__province__code="DEMO", name_en__startswith="Fictional", is_active=True)
            if matches.count() != 1:
                raise CommandError(f"Expected one existing fictional demo village: {code}. No data changed.")
            villages.append(matches.get())
        images = {}
        for _, _, key, _ in PHOTO_TARGETS:
            path = options["image_dir"] / f"{key}.png"
            try:
                with Image.open(path) as candidate:
                    candidate.verify()
                data = path.read_bytes()
                if not data.startswith(b"\x89PNG\r\n\x1a\n") or len(data) > settings.TNK_MAX_UPLOAD_BYTES:
                    raise ValueError("Expected a PNG within the configured upload limit")
                images[key] = data
            except (OSError, ValueError) as error:
                raise CommandError(f"Invalid demo photo {path}: {error}") from error

        # File storage does not roll back with SQL. Track only this attempt's files.
        stored = []
        created = 0
        skipped = 0
        helper = OriginalDemoCommand()
        try:
            with transaction.atomic():
                for quarter in range(1, 5):
                    end_month = quarter * 3
                    period, _ = ReportingPeriod.objects.get_or_create(
                        year=SHOWCASE_YEAR, quarter=quarter,
                        defaults={"start_date": date(SHOWCASE_YEAR, end_month - 2, 1),
                                  "end_date": date(SHOWCASE_YEAR, end_month, monthrange(SHOWCASE_YEAR, end_month)[1]),
                                  "submission_due_date": date(SHOWCASE_YEAR, end_month, monthrange(SHOWCASE_YEAR, end_month)[1]) + timedelta(days=30),
                                  "is_open": True, "is_locked": False},
                    )
                    period = ReportingPeriod.objects.select_for_update().get(pk=period.pk)
                    for index, (village, (_, author_key, reviewer_key)) in enumerate(zip(villages, VILLAGES)):
                        if TNKReport.objects.filter(village=village, reporting_period=period).exists():
                            skipped += 1
                            continue  # Never refill, reopen, or overwrite a report a user may have edited.
                        report = create_report(village=village, reporting_period=period, prepared_by=users[author_key])
                        helper._all_entries(report, users, offset=index * 10 + quarter * 4)
                        self._vary_entries(report, index, quarter)
                        self._photos(report, images, quarter, stored)
                        helper._complete(report, users[author_key])
                        recalculate_report_progress(report)
                        self._workflow(report, users[author_key], users[reviewer_key], users["roko"], index, quarter)
                        created += 1
        except Exception:
            for storage, name in stored:
                storage.delete(name)
            raise
        self.stdout.write(self.style.SUCCESS(
            f"Demo showcase complete: {created} new reports, {created * len(PHOTO_TARGETS)} synthetic photos; {skipped} existing reports untouched."
        ))
        self.stdout.write("Use demo_roko_tui or demo_roko_veivuke. Select Fictional Test Province and year 2100. Passwords and assignments were not changed.")

    def _vary_entries(self, report, index, quarter):
        # Only newly created, report-scoped records are varied. Shared historical masters stay intact.
        CropProductionSnapshot.objects.filter(report=report).update(
            quantity_harvested=Decimal(4200 + index * 600 + quarter * 250),
            quantity_consumed=Decimal(1700), quantity_lost=Decimal(300),
            quantity_sold=Decimal(2200 + index * 600 + quarter * 250),
            estimated_sales_value=Decimal((2200 + index * 600 + quarter * 250) * 6),
        )
        HealthConditionSnapshot.objects.filter(report=report).update(new_cases=2 + index * 3 + quarter, recovered_cases=2 + quarter)
        FoodSecuritySnapshot.objects.filter(report=report).update(households_with_food_shortage=max(1, 8 + index * 2 - quarter))
        for interruption in WaterInterruption.objects.filter(report=report):
            interruption.duration_hours = Decimal(2 + index * 4 + quarter)
            interruption.restored_date = interruption.start_date + timedelta(hours=int(interruption.duration_hours))
            interruption.save(update_fields=("duration_hours", "restored_date"))

    def _photos(self, report, images, quarter, stored):
        stage = ("before", "progress", "after", "observation")[quarter - 1]
        for section, entry_key, key, label in PHOTO_TARGETS:
            instance = entry_queryset(get_entry_config(section, entry_key), report).first()
            if instance is None:
                raise CommandError(f"Missing seeded entry: {section}/{entry_key}")
            save_record_photos(
                user=report.prepared_by, report=report, section_code=section, entry_key=entry_key,
                identifier=str(getattr(instance, "uuid", instance.pk)),
                rows=[{"image": SimpleUploadedFile(f"demo-{report.village.code}-2100-q{quarter}-{key}.png", images[key], content_type="image/png"),
                       "caption": f"DEMO - AI-generated sample, not actual evidence: {label} (Q{quarter}).",
                       "captured_at": timezone.now(), "stage": stage, "confidentiality_level": "restricted"}],
            )
            photo = RecordPhoto.objects.select_related("document").get(report=report, section_code=section, entry_key=entry_key)
            stored.append((photo.document.file.storage, photo.document.file.name))

    def _workflow(self, report, author, reviewer, roko, index, quarter):
        if quarter == 4 and index == 2:
            return  # One editable report for trying the forms and uploads.
        for action in ("mark_ready", "submit"):
            transition_report(report=report, user=author, action=action)
        if quarter == 3 and index == 2:
            return
        transition_report(report=report, user=reviewer, action="start_tikina_review")
        if quarter == 3 and index == 1:
            return
        transition_report(report=report, user=reviewer, action="forward")
        if quarter == 4 and index == 1:
            return
        transition_report(report=report, user=roko, action="approve", acknowledged=True,
                          comment="Fictional demonstration approval only; figures and images are synthetic.")
