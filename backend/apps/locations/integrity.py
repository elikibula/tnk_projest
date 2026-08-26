from collections import defaultdict

from django.apps import apps
from django.db.models import F

from .models import Province, Tikina, Village
from .reconciliation import normalise


def location_integrity():
    """Read-only checks, including all foreign keys into the existing hierarchy."""
    issues = []
    for model, parent in ((Province, None), (Tikina, "province"), (Village, "tikina")):
        groups = defaultdict(list)
        fields = ["pk", "name_en", "is_active"] + ([f"{parent}_id"] if parent else [])
        for row in model.objects.values(*fields):
            groups[(row.get(f"{parent}_id"), normalise(row["name_en"]))].append(row["pk"])
        for key, ids in groups.items():
            if len(ids) > 1:
                issues.append(f"DUPLICATE_DATABASE_RECORD {model._meta.label}: parent={key[0]}, normalised_name={key[1]!r}, IDs={ids}")
            if not key[1]:
                issues.append(f"BLANK_NAME {model._meta.label}: IDs={ids}")
        if parent:
            ids = list(model.objects.filter(is_active=True, **{f"{parent}__is_active": False}).values_list("pk", flat=True))
            if ids:
                issues.append(f"INACTIVE_PARENT {model._meta.label}: active children {ids}")
    for model in apps.get_models():
        names = {field.name for field in model._meta.fields}
        for field in model._meta.fields:
            if getattr(field, "related_model", None) in (Province, Tikina, Village):
                invalid = model.objects.exclude(**{f"{field.attname}__in": field.related_model.objects.values("pk")})
                if field.null:
                    invalid = invalid.filter(**{f"{field.attname}__isnull": False})
                ids = list(invalid.values_list("pk", flat=True))
                if ids:
                    issues.append(f"BROKEN_LOCATION_FK {model._meta.label}.{field.name}: IDs={ids}")
        if {"report", "village"} <= names and model._meta.get_field("report").related_model._meta.label == "reporting.TNKReport":
            ids = list(model.objects.exclude(village_id=F("report__village_id")).values_list("pk", flat=True))
            if ids:
                issues.append(f"REPORT_VILLAGE_CONFLICT {model._meta.label}: IDs={ids}")
    # Generic checks for redundant location fields, e.g. analytics indicator scopes.
    from apps.analytics.models import IndicatorValue
    for filters, comparison, label in (
        ({"village__isnull": False, "tikina__isnull": False}, {"tikina_id": F("village__tikina_id")}, "village/tikina"),
        ({"village__isnull": False, "province__isnull": False}, {"province_id": F("village__tikina__province_id")}, "village/province"),
        ({"tikina__isnull": False, "province__isnull": False}, {"province_id": F("tikina__province_id")}, "tikina/province"),
    ):
        ids = list(IndicatorValue.objects.filter(**filters).exclude(**comparison).values_list("pk", flat=True))
        if ids:
            issues.append(f"ANALYTICS_PARENT_CONFLICT {label}: IDs={ids}")
    return issues
