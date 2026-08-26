from collections import Counter
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.locations.reconciliation import CONTROL_WARNING, MODELS, apply_seed, read_seed, reconcile, write_report


class Command(BaseCommand):
    help = "Reconcile the working Fiji location seed; never writes to the database without --apply."

    def add_arguments(self, parser):
        parser.add_argument("--file", required=True)
        modes = parser.add_mutually_exclusive_group()
        modes.add_argument("--dry-run", action="store_true")
        modes.add_argument("--apply", action="store_true")
        parser.add_argument("--province")
        parser.add_argument("--report-output")
        parser.add_argument("--verbose", action="store_true")

    def handle(self, *args, **options):
        if options["report_output"] and Path(options["file"]).resolve() == Path(options["report_output"]).resolve():
            raise CommandError("Reconciliation output must not overwrite the source CSV.")
        self.stdout.write("Reading working location seed...")
        seed = read_seed(options["file"])
        nodes, events, before = reconcile(seed, options["province"])
        self.stdout.write("TNK Insight Location Reconciliation\n===================================")
        self.stdout.write(f"Source SHA256: {seed.digest}")
        for level in MODELS:
            self.stdout.write(f"CSV {level}: {seed.totals.get(level, 0)} | Existing {level}: {before[level]}")
        self.stdout.write(self.style.WARNING("WARNING: " + CONTROL_WARNING))
        if seed.totals != {"province": 14, "tikina": 189, "village": 1172}:
            self.stdout.write(self.style.WARNING("CSV differs from the expected full working-seed totals (14 / 189 / 1172). This may be a subset; verify before applying."))
        if options["province"]:
            self.stdout.write(f"Scope: {options['province']} (national counts above refer to the complete file).")
        for category, count in sorted(Counter(row["category"] for row in events).items()):
            self.stdout.write(f"{category}: {count}")
        reviews = [row for row in seed.rows if row["validation_status"] == "REVIEW"]
        for row in reviews:
            self.stdout.write(self.style.WARNING(f"REVIEW Row {row['line']}: {row['province']} / {row['tikina']} / {row['village']} — {row['notes']}"))
        for issue in seed.issues:
            self.stdout.write(self.style.ERROR(f"Rows {issue['csv_lines']}: {issue['category']} — {issue['detail']}"))
        if options["verbose"]:
            for row in events:
                self.stdout.write(f"{row['category']} [{row['level']}] {row.get('province', '')}/{row.get('tikina', '')}/{row.get('village', '')}: {row['detail']}")
        if options["report_output"]:
            try:
                write_report(options["report_output"], events)
            except OSError as error:
                raise CommandError(f"Cannot write reconciliation report; database unchanged: {error}") from error
            self.stdout.write(f"Reconciliation CSV: {options['report_output']}")
        if seed.issues:
            raise CommandError("CSV validation failed; no database changes were made.")
        if not options["apply"]:
            self.stdout.write(self.style.SUCCESS("DRY RUN COMPLETE — No database changes were made."))
            return
        nodes, events, before, created = apply_seed(seed, options["province"])
        self.stdout.write(self.style.SUCCESS("IMPORT COMPLETE — additive only; existing records unchanged."))
        for level, model in MODELS.items():
            self.stdout.write(f"Created {level}: {created.get(level, 0)} | Existing before: {before[level]} | Total after: {model.objects.count()}")
        self.stdout.write(f"Review/conflict nodes skipped: {sum(node.action == 'SKIP' for node in nodes.values())}")
