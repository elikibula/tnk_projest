from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.reporting.models import ReportingPeriod
from apps.workflow.services import archive_report


class Command(BaseCommand):
    help = "Lock a period and archive its locked reports through the authorised workflow service."

    def add_arguments(self, parser):
        parser.add_argument("year", type=int)
        parser.add_argument("quarter", type=int)
        parser.add_argument("--actor", required=True, help="Username of the accountable Roko Tui or System Administrator.")
        parser.add_argument("--reason", required=True, help="Reason retained in each immutable archival action.")
        parser.add_argument("--acknowledge", action="store_true", help="Required digital acknowledgement for archival.")

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            period = ReportingPeriod.objects.select_for_update().get(
                year=options["year"],
                quarter=options["quarter"],
            )
        except ReportingPeriod.DoesNotExist as error:
            raise CommandError("Period not found.") from error
        try:
            actor = get_user_model().objects.get(username=options["actor"], is_active=True)
        except get_user_model().DoesNotExist as error:
            raise CommandError("The accountable active user was not found.") from error
        if not options["acknowledge"]:
            raise CommandError("Archival requires --acknowledge.")
        if period.reports.exclude(status__in=("locked", "archived")).exists():
            raise CommandError("All reports must be locked before archiving the period.")
        try:
            for report in period.reports.filter(status="locked").select_related("village"):
                archive_report(
                    report=report,
                    user=actor,
                    comment=options["reason"],
                    acknowledged=True,
                )
        except (PermissionDenied, ValidationError) as error:
            raise CommandError(str(error)) from error
        period.is_open = False
        period.is_locked = True
        period.save(update_fields=("is_open", "is_locked", "updated_at"))
        self.stdout.write(self.style.SUCCESS(f"Archived {period}."))
