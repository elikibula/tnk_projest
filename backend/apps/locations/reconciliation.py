"""Conservative, additive reconciliation of the working Fiji location seed.

Names are matched only within their full parent path. Similarity produces review
items, never aliases. Existing objects are never updated or deleted.
"""
import csv
import hashlib
import io
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

from django.core.management.base import CommandError
from django.db import connection, transaction

from .models import Province, Tikina, Village


DIVISIONS = {
    "Central": ("Naitasiri", "Namosi", "Rewa", "Serua", "Tailevu"),
    "Eastern": ("Kadavu", "Lau", "Lomaiviti"),
    "Northern": ("Bua", "Cakaudrove", "Macuata"),
    "Western": ("Ba", "Nadroga-Navosa", "Ra"),
}
PROVINCES = {name.casefold(): division for division, names in DIVISIONS.items() for name in names}
MODELS = {"province": Province, "tikina": Tikina, "village": Village}
COLUMNS = ("division", "province", "tikina", "village", "province_code", "tikina_key", "village_key", "is_active", "validation_status", "notes", "source_url")
REPORT_COLUMNS = ("category", "level", "province", "tikina", "village", "csv_lines", "db_ids", "db_names", "action", "detail", "validation_status", "notes", "source_url", "division", "source_keys")
CONTROL_WARNING = (
    "Official national reference indicates 190 districts/Tikina, while the supplied working detailed seed contains 189. "
    "Do not assume which Tikina is missing or differently classified. Reconcile against the current iTaukei Affairs master register."
)


def clean_name(value):
    return " ".join((value or "").split())


def normalise(value):
    return clean_name(value).casefold()


def similar(left, right):
    # Administrative suffix removal is a REVIEW hint only, never an exact match.
    suffix = r"\s+(province|district|tikina|village|koro)$"
    left, right = normalise(left), normalise(right)
    if re.sub(suffix, "", left) == re.sub(suffix, "", right):
        return True
    return min(len(left), len(right)) >= 4 and SequenceMatcher(None, left, right).ratio() >= 0.82


def generated_code(level, path):
    # Internal, deterministic codes fit existing 20-character fields. They are NOT official codes.
    return "S" + level[0].upper() + hashlib.sha256("\x1f".join(path).encode()).hexdigest()[:18].upper()


@dataclass
class Node:
    level: str
    path: tuple
    names: tuple
    rows: list = field(default_factory=list)
    existing: object = None
    action: str = "SKIP"
    category: str = "REQUIRES_MANUAL_REVIEW"
    safe: bool = False
    code: str = ""
    active: bool = True


@dataclass
class Seed:
    rows: list
    nodes: dict
    issues: list
    digest: str

    @property
    def totals(self):
        return dict(Counter(node.level for node in self.nodes.values()))


def event(category, level="csv", names=(), rows=(), matches=(), action="SKIP", detail=""):
    return {
        "category": category, "level": level,
        **dict(zip(("province", "tikina", "village"), names)),
        "csv_lines": ";".join(str(row["line"]) for row in rows),
        "db_ids": ";".join(str(item.pk) for item in matches),
        "db_names": ";".join(item.name_en for item in matches),
        "action": action, "detail": detail,
        **{key: " | ".join(dict.fromkeys(row.get(key, "") for row in rows if row.get(key))) for key in ("validation_status", "notes", "source_url", "division")},
        "source_keys": " | ".join(dict.fromkeys(f"{row.get('province_code', '')};{row.get('tikina_key', '')};{row.get('village_key', '')}" for row in rows)),
    }


def read_seed(filename):
    path = Path(filename)
    nodes, rows, issues = {}, [], []
    try:
        content = path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        with io.StringIO(content.decode("utf-8-sig"), newline="") as source:
            reader = csv.DictReader(source, strict=True)
            if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
                raise CommandError("CSV has missing or duplicate column headers.")
            missing = set(COLUMNS) - set(reader.fieldnames)
            if missing:
                raise CommandError("Missing required columns: " + ", ".join(sorted(missing)))
            for raw in reader:
                row = {key: (raw.get(key) or "").strip() for key in COLUMNS}
                row["line"] = reader.line_num
                rows.append(row)
                errors = []
                if None in raw or any(raw.get(key) is None for key in COLUMNS):
                    errors.append("Wrong number of CSV fields.")
                for key in ("province", "tikina", "village"):
                    row[key] = clean_name(row[key])
                    if not row[key] or len(row[key]) > 120:
                        errors.append(f"{key} must contain 1–120 characters.")
                expected_division = PROVINCES.get(normalise(row["province"]))
                if not expected_division:
                    errors.append("Province is outside the expected 14-province seed (Rotuma is not included).")
                elif normalise(row["division"]) != normalise(expected_division):
                    errors.append("Division/province relationship conflicts with the expected mapping.")
                if row["validation_status"] not in {"SOURCE_SEED", "REVIEW"}:
                    errors.append("Unknown validation_status; expected SOURCE_SEED or REVIEW.")
                if row["is_active"].casefold() not in {"true", "false", "1", "0"}:
                    errors.append("is_active must be True, False, 1 or 0.")
                if not row["province_code"] or len(row["province_code"]) > 20:
                    errors.append("province_code must contain 1–20 characters.")
                if not row["tikina_key"] or not row["village_key"]:
                    errors.append("Matching helper keys must not be blank.")
                names = tuple(row[key] for key in ("province", "tikina", "village"))
                if errors:
                    issues.append(event("CSV_ERROR", names=names, rows=[row], detail=" ".join(errors)))
                    continue
                for depth, level in enumerate(MODELS, 1):
                    key = (level, tuple(normalise(name) for name in names[:depth]))
                    nodes.setdefault(key, Node(level, key[1], names[:depth])).rows.append(row)
    except (OSError, UnicodeError, csv.Error) as error:
        raise CommandError(f"Cannot parse CSV: {error}") from error
    if not rows:
        raise CommandError("CSV contains no location rows.")
    for node in nodes.values():
        if node.level == "village" and len(node.rows) > 1:
            issues.append(event("DUPLICATE_CSV_RECORD", node.level, node.names, node.rows, detail="Duplicate normalised province/tikina/village path."))
        if node.level == "province" and len({normalise(row["province_code"]) for row in node.rows}) > 1:
            issues.append(event("CSV_ERROR", node.level, node.names, node.rows, detail="Province has conflicting province codes."))
    for field_name, depth in (("province_code", 1), ("tikina_key", 2), ("village_key", 3)):
        keys = defaultdict(list)
        for row in rows:
            keys[normalise(row[field_name])].append(row)
        for key, keyed_rows in keys.items():
            identities = {tuple(normalise(row[name]) for name in ("province", "tikina", "village")[:depth]) for row in keyed_rows}
            if key and len(identities) > 1:
                issues.append(event("PARENT_LOCATION_CONFLICT", rows=keyed_rows, detail=f"CSV {field_name} is reused for different full identities. No key is used to merge records."))
    return Seed(rows, nodes, issues, digest)


def database_locations():
    return {
        "province": list(Province.objects.order_by("pk")),
        "tikina": list(Tikina.objects.select_related("province").order_by("pk")),
        "village": list(Village.objects.select_related("tikina__province").order_by("pk")),
    }


def db_names(level, item):
    if level == "province":
        return (item.name_en,)
    if level == "tikina":
        return (item.province.name_en, item.name_en)
    return (item.tikina.province.name_en, item.tikina.name_en, item.name_en)


def reconcile(seed, province=None):
    database = database_locations()
    index, by_parent = defaultdict(list), defaultdict(list)
    for level, items in database.items():
        for item in items:
            path = tuple(normalise(name) for name in db_names(level, item))
            index[(level, path)].append(item)
            by_parent[(level, path[:-1])].append(item)
    nodes = {key: Node(node.level, node.path, node.names, list(node.rows)) for key, node in seed.nodes.items() if not province or node.path[0] == normalise(province)}
    if province and not nodes:
        raise CommandError(f"Province {province!r} is not present in the CSV.")
    events = list(seed.issues)
    for (level, path), items in index.items():
        if len(items) > 1:
            events.append(event("DUPLICATE_DATABASE_RECORD", level, db_names(level, items[0]), matches=items, detail="Duplicate normalised full path; IDs are preserved and affected imports are blocked."))
    # Parent-first traversal, independent of CSV ordering.
    for level in MODELS:
        for (node_level, path), node in nodes.items():
            if node_level != level:
                continue
            parent = nodes.get(("province" if level == "tikina" else "tikina", path[:-1])) if level != "province" else None
            source_rows = [row for row in node.rows if row["validation_status"] == "SOURCE_SEED"]
            node.active = any(row["is_active"].casefold() in {"true", "1"} for row in source_rows)
            node.code = node.rows[0]["province_code"] if level == "province" else generated_code(level, path)
            matches = index.get((level, path), [])
            details = []
            if len(matches) > 1:
                node.category = "DUPLICATE_DATABASE_RECORD"
            elif not source_rows:
                node.category = "REQUIRES_MANUAL_REVIEW"
                details.append("REVIEW source row: skipped, including exact existing records. REVIEW-only parents are not created.")
            elif parent and not parent.safe:
                node.category = "REQUIRES_MANUAL_REVIEW"
                details.append("Parent is unresolved or inactive; descendants are not created or reassigned.")
            elif len(matches) == 1:
                node.existing = matches[0]
                node.action = "KEEP"
                node.category = "EXACT_MATCH" if matches[0].name_en == node.names[-1] else "POSSIBLE_CASE_ONLY_MATCH"
                node.safe = matches[0].is_active or not node.active
                if node.category == "POSSIBLE_CASE_ONLY_MATCH":
                    details.append("Case/whitespace-only match reused; stored name and IDs remain unchanged.")
                if matches[0].is_active != node.active:
                    details.append("Active-state difference preserved; no automatic activation/deactivation.")
                    if node.active:
                        node.category = "REQUIRES_MANUAL_REVIEW"
                if level == "province" and matches[0].code != node.code:
                    details.append(f"Existing code {matches[0].code!r} preserved; CSV code {node.code!r} is not forced.")
            else:
                candidates = [item for item in by_parent.get((level, path[:-1]), []) if similar(node.names[-1], item.name_en)]
                # Similarity is only against the pre-existing DB, not other legitimate seed rows.
                if candidates:
                    node.category = "POSSIBLE_SPELLING_VARIANT"
                    matches = candidates
                    details.append("Possible spelling/suffix variant. Administrator must reconcile; never auto-merged.")
                else:
                    relocated = [item for item in database[level] if normalise(item.name_en) == path[-1] and (level, tuple(normalise(name) for name in db_names(level, item))) not in seed.nodes]
                    if relocated:
                        node.category = "PARENT_LOCATION_CONFLICT"
                        matches = relocated
                        details.append("Same name under another parent absent from the seed: possible relocation OR distinct namesake. Review; no move or merge.")
                    else:
                        collisions = [item for item in by_parent.get((level, path[:-1]), []) if normalise(item.code) == normalise(node.code)]
                        if collisions:
                            node.category = "REQUIRES_MANUAL_REVIEW"
                            matches = collisions
                            details.append("Proposed code is already used by another record. No replacement.")
                        else:
                            node.category, node.action, node.safe = f"NEW_{level.upper()}", "CREATE", True
            events.append(event(node.category, level, node.names, node.rows, matches, node.action, " ".join(details)))
            if not index.get((level, path)):
                events.append(event("CSV_RECORD_NOT_IN_DATABASE", level, node.names, node.rows, action=node.action, detail="No exact normalised full-path match; see primary classification."))
    for level, items in database.items():
        for item in items:
            names = db_names(level, item)
            if province and normalise(names[0]) != normalise(province) and not similar(names[0], province):
                continue
            if (level, tuple(normalise(name) for name in names)) not in seed.nodes:
                events.append(event("EXISTING_ONLY", level, names, matches=[item], action="KEEP", detail="Existing database record not matched by this seed. Preserve IDs, names, assignments and history."))
    return nodes, events, {level: len(items) for level, items in database.items()}


def apply_seed(seed, province=None):
    if seed.issues:
        raise CommandError("CSV validation failed. Nothing was imported; resolve all CSV errors first.")
    with transaction.atomic():
        # Prevent concurrent import/admin writes during reconciliation. SQLite's
        # write lock is obtained by the first INSERT; a racing writer rolls back.
        if connection.vendor == "postgresql":
            with connection.cursor() as cursor:
                cursor.execute("LOCK TABLE locations_province, locations_tikina, locations_village IN SHARE ROW EXCLUSIVE MODE")
        elif connection.vendor != "sqlite":
            raise CommandError("Apply supports the project's SQLite/PostgreSQL databases only.")
        nodes, events, before = reconcile(seed, province)
        created = Counter()
        for level in MODELS:
            for (node_level, path), node in nodes.items():
                if node_level != level or node.action != "CREATE":
                    continue
                parent = {}
                if level != "province":
                    parent_level = "province" if level == "tikina" else "tikina"
                    parent[parent_level] = nodes[(parent_level, path[:-1])].existing
                item, was_created = MODELS[level].objects.get_or_create(**parent, code=node.code, defaults={"name_en": node.names[-1], "is_active": node.active})
                if not was_created and normalise(item.name_en) != path[-1]:
                    raise CommandError("Concurrent code/name conflict. Entire import rolled back.")
                node.existing = item
                created[level] += int(was_created)
        return nodes, events, before, dict(created)


def write_report(filename, events):
    # Do not execute formulas when an administrator opens an untrusted CSV in Excel.
    def safe_cell(value):
        value = str(value)
        return "'" + value if value.lstrip().startswith(("=", "+", "-", "@")) else value
    with Path(filename).open("x", encoding="utf-8-sig", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows({key: safe_cell(row.get(key, "")) for key in REPORT_COLUMNS} for row in events)
