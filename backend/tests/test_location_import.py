import csv
import io
import tempfile
from datetime import date
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from apps.accounts.models import Role, User, UserLocationAssignment, UserRoleAssignment
from apps.locations.integrity import location_integrity
from apps.locations.models import Province, Tikina, Village
from apps.locations.reconciliation import COLUMNS, apply_seed, read_seed, reconcile
from apps.reporting.models import ReportingPeriod
from apps.reporting.services import create_report


def seed_row(province="Lau", tikina="Lakeba", village="Tubou", **changes):
    from apps.locations.reconciliation import PROVINCES
    codes = {"Lau": "LA", "Ba": "BA", "Bua": "BU", "Rewa": "RE"}
    row = dict(zip(COLUMNS, (PROVINCES.get(province.casefold(), "Unknown"), province, tikina, village, codes.get(province, province[:2].upper()), f"{province}::{tikina}".lower(), f"{province}::{tikina}::{village}".lower(), "True", "SOURCE_SEED", "", "https://example.test/working-seed")))
    row.update(changes)
    return row


class LocationImportTests(TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.source = Path(self.directory.name) / "seed.csv"

    def write_seed(self, rows):
        with self.source.open("w", encoding="utf-8-sig", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
        return read_seed(self.source)

    def command(self, **options):
        output = io.StringIO()
        call_command("import_locations", file=str(self.source), stdout=output, **options)
        return output.getvalue()

    def test_default_and_explicit_dry_run_issue_no_database_writes(self):
        self.write_seed([seed_row()])
        for options in ({}, {"dry_run": True}):
            with CaptureQueriesContext(connection) as queries:
                output = self.command(**options)
            self.assertIn("No database changes", output)
            self.assertFalse(any(query["sql"].lstrip().split()[0].upper() in {"INSERT", "UPDATE", "DELETE", "REPLACE", "CREATE", "ALTER"} for query in queries))
            self.assertEqual(Province.objects.count(), 0)

    def test_apply_creates_parent_first_and_is_idempotent(self):
        self.write_seed([seed_row(), seed_row(village="Nasaqalau")])
        self.assertIn("IMPORT COMPLETE", self.command(apply=True))
        village = Village.objects.get(name_en="Tubou")
        identity = (village.pk, village.uuid, village.code, village.tikina_id, village.tikina.province_id)
        self.assertEqual(village.tikina.name_en, "Lakeba")
        self.assertEqual(village.tikina.province.name_en, "Lau")
        self.assertEqual(len(village.code), 20)
        second = self.command(apply=True)
        self.assertIn("Created village: 0", second)
        village.refresh_from_db()
        self.assertEqual(identity, (village.pk, village.uuid, village.code, village.tikina_id, village.tikina.province_id))
        self.assertEqual((Province.objects.count(), Tikina.objects.count(), Village.objects.count()), (1, 1, 2))

    def test_case_and_whitespace_reuse_preserves_existing_names_codes_and_ids(self):
        province = Province.objects.create(name_en="LAU", code="LAU-OLD")
        tikina = Tikina.objects.create(province=province, name_en=" lakeba  ", code="LEGACY")
        village = Village.objects.create(tikina=tikina, name_en="TUBOU", code="OLD-TUBOU")
        self.write_seed([seed_row()])
        self.assertIn("POSSIBLE_CASE_ONLY_MATCH", self.command(apply=True))
        village.refresh_from_db()
        self.assertEqual((village.name_en, village.code, village.tikina_id), ("TUBOU", "OLD-TUBOU", tikina.pk))
        self.assertEqual(Province.objects.get().name_en, "LAU")

    def test_similar_names_and_suffixes_are_reviewed_not_merged(self):
        Province.objects.create(name_en="Lau Province", code="LAU")
        self.write_seed([seed_row()])
        output = self.command(apply=True)
        self.assertIn("POSSIBLE_SPELLING_VARIANT", output)
        self.assertEqual(Province.objects.count(), 1)
        self.assertEqual(Tikina.objects.count(), 0)
        province = Province.objects.create(name_en="Ba", code="BA")
        tikina = Tikina.objects.create(province=province, name_en="Vuda", code="VUDA")
        Village.objects.create(tikina=tikina, name_en="Viseisei", code="VIS")
        self.write_seed([seed_row("Ba", "Vuda", "Veiseisei")])
        self.assertIn("POSSIBLE_SPELLING_VARIANT", self.command(apply=True))
        self.assertEqual(Village.objects.count(), 1)

    def test_same_names_under_different_parents_remain_distinct(self):
        rows = [seed_row("Lau", "Shared", "Nakorovou"), seed_row("Ba", "Shared", "Nakorovou"), seed_row("Ba", "Other", "Nakorovou")]
        self.write_seed(rows)
        self.command(apply=True)
        self.command(apply=True)
        self.assertEqual(Tikina.objects.filter(name_en="Shared").count(), 2)
        self.assertEqual(Village.objects.filter(name_en="Nakorovou").count(), 3)

    def test_possible_parent_move_is_flagged_and_not_applied(self):
        province = Province.objects.create(name_en="Lau", code="LA")
        parent = Tikina.objects.create(province=province, name_en="Lakeba", code="LAKEBA")
        existing = Village.objects.create(tikina=parent, name_en="Tubou", code="TUBOU")
        self.write_seed([seed_row(tikina="Moala")])
        self.assertIn("PARENT_LOCATION_CONFLICT", self.command(apply=True))
        existing.refresh_from_db()
        self.assertEqual(existing.tikina_id, parent.pk)
        self.assertEqual(Village.objects.count(), 1)

    def test_review_rows_skipped_even_when_exact_and_notes_preserved(self):
        seed = self.write_seed([seed_row(validation_status="REVIEW", notes="Verify official location")])
        nodes, events, _ = reconcile(seed)
        self.assertTrue(all(node.action == "SKIP" for node in nodes.values()))
        self.assertIn("Verify official location", events[0]["notes"])
        self.command(apply=True)
        self.assertEqual(Province.objects.count(), 0)
        self.write_seed([seed_row()])
        self.command(apply=True)
        self.write_seed([seed_row(validation_status="REVIEW", is_active="False")])
        self.command(apply=True)
        self.assertTrue(Village.objects.get().is_active)

    def test_duplicate_csv_and_bad_values_fail_before_writing(self):
        for rows in ([seed_row(), seed_row()], [seed_row(village="")], [seed_row(division="Western")], [seed_row(validation_status="GUESS")], [seed_row(is_active="maybe")], [seed_row(province="Rotuma")]):
            with self.subTest(rows=rows):
                seed = self.write_seed(rows)
                self.assertTrue(seed.issues)
                with self.assertRaises(CommandError):
                    self.command(apply=True)
                self.assertEqual(Province.objects.count(), 0)
        self.source.write_text("province,tikina,village\nLau,Lakeba,Tubou\n", encoding="utf-8")
        with self.assertRaisesMessage(CommandError, "Missing required columns"):
            read_seed(self.source)

    def test_reused_helper_keys_cannot_reparent(self):
        seed = self.write_seed([seed_row(), seed_row(tikina="Moala", village="Other", village_key="lau::lakeba::tubou")])
        self.assertTrue(any(item["category"] == "PARENT_LOCATION_CONFLICT" for item in seed.issues))
        with self.assertRaises(CommandError):
            apply_seed(seed)

    def test_duplicate_database_names_block_only_affected_branch(self):
        Province.objects.create(name_en="Lau", code="LA")
        Province.objects.create(name_en=" LAU ", code="OTHER")
        self.write_seed([seed_row(), seed_row("Ba", "Nailaga", "Nailaga")])
        self.assertIn("DUPLICATE_DATABASE_RECORD", self.command(apply=True))
        self.assertFalse(Tikina.objects.filter(name_en="Lakeba").exists())
        self.assertTrue(Village.objects.filter(name_en="Nailaga").exists())

    def test_atomic_rollback_on_late_failure(self):
        seed = self.write_seed([seed_row()])
        with patch.object(Village.objects, "get_or_create", side_effect=IntegrityError("forced failure")):
            with self.assertRaises(IntegrityError):
                apply_seed(seed)
        self.assertEqual((Province.objects.count(), Tikina.objects.count(), Village.objects.count()), (0, 0, 0))

    def test_existing_reports_assignments_and_inactive_records_unchanged(self):
        self.write_seed([seed_row()])
        self.command(apply=True)
        village = Village.objects.get()
        user = User.objects.create_user(username="author")
        role = Role.objects.create(code=Role.Codes.TURAGA_NI_KORO, name="TNK")
        UserRoleAssignment.objects.create(user=user, role=role)
        assignment = UserLocationAssignment.objects.create(user=user, village=village)
        period = ReportingPeriod.objects.create(year=2026, quarter=2, start_date=date(2026,4,1), end_date=date(2026,6,30), submission_due_date=date(2026,7,15), is_open=True)
        report = create_report(village=village, reporting_period=period, prepared_by=user)
        report_id, assignment_id, village_uuid = report.pk, assignment.pk, village.uuid
        Village.objects.filter(pk=village.pk).update(is_active=False)
        self.write_seed([seed_row(), seed_row("Ba", "Nailaga", "Nailaga")])
        self.command(apply=True)
        report.refresh_from_db(); assignment.refresh_from_db(); village.refresh_from_db()
        self.assertEqual((report.pk, assignment.pk, village.uuid), (report_id, assignment_id, village_uuid))
        self.assertEqual((report.village_id, assignment.village_id), (village.pk, village.pk))
        self.assertFalse(village.is_active)

    def test_inactive_parent_does_not_get_active_children(self):
        Province.objects.create(name_en="Lau", code="LA", is_active=False)
        self.write_seed([seed_row()])
        self.command(apply=True)
        self.assertEqual(Tikina.objects.count(), 0)

    def test_province_filter_and_report_output(self):
        self.write_seed([seed_row(), seed_row("Ba", "Nailaga", "Nailaga")])
        destination = Path(self.directory.name) / "audit.csv"
        self.command(apply=True, province="Lau", report_output=str(destination))
        self.assertEqual(list(Province.objects.values_list("name_en", flat=True)), ["Lau"])
        self.assertIn("source_url", destination.read_text(encoding="utf-8-sig"))
        with self.assertRaises(CommandError):
            self.command(report_output=str(self.source))

    def test_integrity_command_detects_duplicates_and_inactive_parents(self):
        province = Province.objects.create(name_en="Lau", code="LA", is_active=False)
        Tikina.objects.create(province=province, name_en="Lakeba", code="A")
        Tikina.objects.create(province=province, name_en=" LAKEBA ", code="B")
        issues = location_integrity()
        self.assertTrue(any("DUPLICATE_DATABASE_RECORD" in issue for issue in issues))
        self.assertTrue(any("INACTIVE_PARENT" in issue for issue in issues))
        with self.assertRaises(CommandError):
            call_command("check_locations", stdout=io.StringIO())

    def test_full_supplied_seed_in_isolated_database_and_four_divisions(self):
        seed = read_seed(settings.BASE_DIR / "data" / "tnk_fiji_locations_master.csv")
        self.assertEqual(seed.totals, {"province":14,"tikina":189,"village":1172})
        _, _, _, created = apply_seed(seed)
        self.assertEqual(created, {"province":14,"tikina":189,"village":1169})
        self.assertEqual(apply_seed(seed)[3], {})
        for province, tikina, village in (("Lau","Lakeba","Tubou"), ("Ba","Nailaga","Nailaga"), ("Bua","Bua","Bua"), ("Rewa","Rewa","Lomanikoro")):
            self.assertTrue(Village.objects.filter(name_en=village,tikina__name_en=tikina,tikina__province__name_en=province).exists(), (province,tikina,village))
        self.assertEqual(location_integrity(), [])

    def test_imported_locations_appear_in_admin_mobile_and_analytics(self):
        from apps.administration.forms import AdministrativeUserForm
        from apps.analytics.decision_support import child_locations
        from apps.mobile_api.serializers import VillageSerializer
        self.write_seed([seed_row(), seed_row("Ba", "Nailaga", "Nailaga")])
        self.command(apply=True)
        admin = User.objects.create_superuser(username="location-admin", password="test-only")
        form = AdministrativeUserForm(actor=admin)
        self.assertEqual(form.fields["village"].queryset.count(), 2)
        province = Province.objects.get(name_en="Lau")
        tikina = province.tikina.get()
        self.client.force_login(admin)
        response = self.client.get(reverse("administration:location_options"), {"province": province.pk})
        self.assertEqual([row["name_en"] for row in response.json()["results"]], ["Lakeba"])
        response = self.client.get(reverse("administration:location_options"), {"tikina": tikina.pk})
        self.assertEqual([row["name_en"] for row in response.json()["results"]], ["Tubou"])
        payload = VillageSerializer(tikina.villages.get()).data
        self.assertEqual(str(payload["province_uuid"]), str(province.uuid))
        self.assertEqual([item.name_en for item in child_locations(admin, province)], ["Lakeba"])

    def test_location_options_reject_invalid_ids_and_inactive_parents(self):
        self.write_seed([seed_row()])
        self.command(apply=True)
        admin = User.objects.create_superuser(username="selector-admin", password="test-only")
        self.client.force_login(admin)
        url = reverse("administration:location_options")
        self.assertEqual(self.client.get(url, {"province": "invalid"}).status_code, 400)
        province = Province.objects.get()
        Province.objects.filter(pk=province.pk).update(is_active=False)
        self.assertEqual(self.client.get(url, {"province": province.pk}).json()["results"], [])

    def test_report_output_never_overwrites_existing_files_or_writes_database_on_failure(self):
        self.write_seed([seed_row()])
        output = Path(self.directory.name) / "existing.csv"
        output.write_text("keep me", encoding="utf-8")
        with self.assertRaises(CommandError):
            self.command(apply=True, report_output=str(output))
        self.assertEqual(output.read_text(encoding="utf-8"), "keep me")
        self.assertEqual(Province.objects.count(), 0)

    def test_existing_code_collision_is_not_replaced(self):
        Province.objects.create(name_en="Existing Province", code="LA")
        self.write_seed([seed_row()])
        self.command(apply=True)
        self.assertEqual(Province.objects.get().name_en, "Existing Province")
        self.assertEqual(Village.objects.count(), 0)

    def test_reconciliation_query_count_is_bounded_not_per_csv_row(self):
        seed = self.write_seed([seed_row(village=f"Village {index}") for index in range(100)])
        with self.assertNumQueries(3):
            reconcile(seed)

    def test_sqlite_backup_is_consistent_and_refuses_overwrite(self):
        import importlib.util
        import sqlite3
        module_path = settings.BASE_DIR.parent / "scripts" / "backup_tnk_sqlite.py"
        spec = importlib.util.spec_from_file_location("backup_tnk_sqlite", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        source = Path(self.directory.name) / "source.sqlite3"
        target = Path(self.directory.name) / "backup.sqlite3"
        with sqlite3.connect(source) as db:
            db.execute("CREATE TABLE evidence (value TEXT)")
            db.execute("INSERT INTO evidence VALUES ('preserve')")
        db.close()
        module.backup_sqlite(source, target)
        with sqlite3.connect(target) as restored:
            self.assertEqual(restored.execute("SELECT value FROM evidence").fetchone()[0], "preserve")
        restored.close()
        with self.assertRaises(FileExistsError):
            module.backup_sqlite(source, target)
        with self.assertRaises(ValueError):
            module.backup_sqlite(source, source)
