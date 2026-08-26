from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

from apps.locations.integrity import location_integrity
from apps.locations.models import Province, Tikina, Village


class Command(BaseCommand):
    help = "Read-only hierarchy, duplicate, foreign-key and active-parent checks."

    def handle(self, *args, **options):
        self.stdout.write("TNK Insight Location Integrity\nProvince | Tikina | Villages")
        for row in Province.objects.annotate(tikina_count=Count("tikina", distinct=True), village_count=Count("tikina__villages", distinct=True)).order_by("name_en"):
            self.stdout.write(f"{row.name_en} | {row.tikina_count} | {row.village_count}")
        self.stdout.write(f"TOTAL: {Province.objects.count()} provinces | {Tikina.objects.count()} Tikina | {Village.objects.count()} villages")
        issues = location_integrity()
        for issue in issues:
            self.stdout.write(self.style.WARNING(issue))
        if issues:
            raise CommandError(f"{len(issues)} integrity issue(s); no data was changed.")
        self.stdout.write(self.style.SUCCESS("No location integrity issues found. No data was changed."))
