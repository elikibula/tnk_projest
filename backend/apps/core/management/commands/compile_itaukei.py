import sys
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Compile the edited iTaukei django.po catalogue into django.mo."

    def handle(self, *args, **options):
        project_root = Path(settings.BASE_DIR).parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        try:
            from scripts.compile_po import read_catalog, write_mo

            source = settings.BASE_DIR / "locale" / "fj" / "LC_MESSAGES" / "django.po"
            destination = source.with_suffix(".mo")
            catalog = read_catalog(source)
            write_mo(catalog, destination)
        except (OSError, SyntaxError, ValueError) as error:
            raise CommandError(f"Could not compile the iTaukei catalogue: {error}") from error
        self.stdout.write(self.style.SUCCESS(f"Compiled {len(catalog)} iTaukei messages. Restart the Django server to load the changes."))
