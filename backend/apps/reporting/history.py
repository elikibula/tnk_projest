from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from django.db import models, transaction
from django.utils import timezone

from apps.reporting.models import ReportMasterSnapshot

from .section_registry import SECTION_ENTRIES


MASTER_ENTRY_CONFIGS = frozenset(
    {
        ("village_profile", "village"),
        ("leadership_governance", "person"),
        ("leadership_governance", "appointment"),
        ("leadership_governance", "committee"),
        ("population_households", "household"),
        ("housing_assets", "asset"),
        ("water", "source"),
        ("sanitation_waste", "facility"),
        ("energy", "energy_asset"),
        ("business_finance", "business"),
        ("business_finance", "account"),
        ("ivdp_projects", "project"),
        ("ivdp_projects", "milestone"),
        ("ivdp_projects", "risk"),
        ("climate_disaster", "preparedness"),
        ("climate_disaster", "centre"),
        ("traditional_culture", "unit"),
        ("traditional_culture", "title"),
        ("traditional_culture", "knowledge"),
    }
)


def is_master_entry(section_code, entry_key):
    return (section_code, entry_key) in MASTER_ENTRY_CONFIGS


def _json_value(value):
    if isinstance(value, models.Model):
        return {"id": str(value.pk), "label": str(value)}
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, (Decimal, UUID)):
        return str(value)
    if hasattr(value, "name") and hasattr(value, "storage"):
        return Path(value.name).name if value.name else ""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def snapshot_values(config, instance):
    values = {}
    for field_name in config.fields:
        if hasattr(instance, field_name):
            values[field_name] = _json_value(getattr(instance, field_name))
    return values


@transaction.atomic
def capture_master_snapshots(report):
    if not report.is_editable:
        raise ValueError("Master snapshots can only be captured from an editable report.")
    from .section_entries import entry_queryset, entry_summary

    ReportMasterSnapshot.objects.filter(report=report).delete()
    snapshots = []
    for section_code, configs in SECTION_ENTRIES.items():
        for config in configs:
            if not is_master_entry(section_code, config.key):
                continue
            for instance in entry_queryset(config, report).iterator():
                identifier = getattr(instance, "uuid", instance.pk)
                snapshots.append(
                    ReportMasterSnapshot(
                        report=report,
                        section_code=section_code,
                        entry_key=config.key,
                        source_model=instance._meta.label,
                        source_identifier=str(identifier),
                        summary=entry_summary(config, instance)[:255],
                        values=snapshot_values(config, instance),
                    )
                )
    ReportMasterSnapshot.objects.bulk_create(snapshots)
    report.master_snapshot_captured_at = timezone.now()
    return snapshots


def section_code_for(config):
    return next(
        section_code
        for section_code, configs in SECTION_ENTRIES.items()
        if config in configs
    )


def snapshot_rows(config, report):
    section_code = section_code_for(config)
    return [
        {
            "object": None,
            "summary": snapshot.summary,
            "public_id": snapshot.source_identifier,
            "snapshot_values": snapshot.values,
        }
        for snapshot in report.master_snapshots.filter(
            section_code=section_code,
            entry_key=config.key,
        )[:100]
    ]
