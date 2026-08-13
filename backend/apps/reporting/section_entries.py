from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import F, Q

from apps.accounts.permissions import REPORT_AUTHOR_ROLE_CODES, user_has_any_role
from apps.audit.services import record_event
from apps.core.historical import close_and_replace, supports_close_and_replace
from apps.reporting.models import ReportSectionStatus, TNKReport
from apps.reporting.selectors import reports_for_user
from .section_registry import EntryConfig


def entry_queryset(config: EntryConfig, report: TNKReport):
    model = config.model
    names = {field.name for field in model._meta.fields}
    queryset = model._default_manager.all()
    if model._meta.label == "locations.Village":
        scoped = queryset.filter(pk=report.village_id)
    elif "report" in names:
        scoped = queryset.filter(report=report)
    elif "reporting_period" in names and "village" in names:
        scoped = queryset.filter(village=report.village, reporting_period=report.reporting_period)
    elif "village" in names:
        scoped = queryset.filter(village=report.village)
    elif "home_village" in names:
        scoped = queryset.filter(home_village=report.village)
    else:
        relation_filters = {
            "account": Q(account__village=report.village),
            "water_source": Q(water_source__village=report.village),
            "facility": Q(facility__village=report.village),
            "project": Q(project__village=report.village),
            "traditional_unit": Q(traditional_unit__village=report.village),
            "meeting": Q(meeting__report=report),
            "committee": Q(committee__village=report.village),
        }
        scoped = queryset.none()
        for field_name, condition in relation_filters.items():
            if field_name in names:
                scoped = queryset.filter(condition)
                break
    return effective_period_queryset(config, scoped, report)


def effective_period_queryset(config, queryset, report):
    """Best-effort period resolution for legacy reports without immutable snapshots."""
    start = report.reporting_period.start_date
    end = report.reporting_period.end_date
    label = config.model._meta.label
    if label == "governance.OfficialAppointment":
        return queryset.filter(effective_from__lte=end).filter(Q(effective_to__isnull=True) | Q(effective_to__gte=start))
    if label == "governance.VillageCommittee":
        return queryset.filter(Q(formed_date__isnull=True) | Q(formed_date__lte=end)).filter(Q(dissolved_date__isnull=True) | Q(dissolved_date__gte=start))
    if label == "population.Household":
        return queryset.filter(effective_from__lte=end).filter(Q(effective_to__isnull=True) | Q(effective_to__gte=start))
    if label == "economy.VillageBusiness":
        return queryset.filter(Q(start_date__isnull=True) | Q(start_date__lte=end)).filter(Q(closure_date__isnull=True) | Q(closure_date__gte=start))
    if label == "infrastructure.VillageAsset":
        return queryset.filter(Q(acquisition_date__isnull=True) | Q(acquisition_date__lte=end))
    if label == "infrastructure.VillageEnergyAsset":
        return queryset.filter(Q(installation_date__isnull=True) | Q(installation_date__lte=end))
    if label == "projects.IVDPProject":
        return queryset.filter(Q(planned_start_date__isnull=True) | Q(planned_start_date__lte=end))
    if label == "infrastructure.WaterQualityTest":
        return queryset.filter(test_date__range=(start, end))
    return queryset


def entry_summary(config, instance):
    label = instance._meta.label
    if label == "governance.OfficialAppointment":
        return f"{instance.person} — {instance.role}"
    if label == "culture.TraditionalTitleAppointment":
        return f"{instance.person} — {instance.title.title_name}"
    preferred_fields = ("name_en", "full_name", "name", "title", "business_name", "project_name", "source_name", "asset_name", "household_code", "decision", "incident_type", "movement_type", "visit_type", "account_type", "hazard_type", "knowledge_name", "title_name", "energy_source", "toilet_type", "structure_type")
    return next(
        (
            str(getattr(instance, field))
            for field in preferred_fields
            if hasattr(instance, field) and getattr(instance, field)
        ),
        config.display_label,
    )


def entry_rows(config, report):
    from .history import is_master_entry, section_code_for, snapshot_rows

    section_code = section_code_for(config)
    if report.master_snapshot_captured_at and not report.is_editable and is_master_entry(section_code, config.key):
        return snapshot_rows(config, report)
    rows = []
    for instance in entry_queryset(config, report)[:100]:
        summary = entry_summary(config, instance)
        rows.append({"object": instance, "summary": summary, "public_id": getattr(instance, "uuid", instance.pk)})
    return rows


def bind_report_context(instance, report, user):
    names = {field.name for field in instance._meta.fields}
    if "report" in names:
        instance.report = report
    if "village" in names:
        instance.village = report.village
    if "home_village" in names:
        instance.home_village = report.village
    if "reporting_period" in names:
        instance.reporting_period = report.reporting_period
    if "created_by" in names and not instance.pk:
        instance.created_by = user
    if "updated_by" in names:
        instance.updated_by = user


def validate_entry_period(instance, report):
    period = report.reporting_period
    date_fields = ("measurement_date", "meeting_date", "visit_date", "movement_date", "collection_date", "reporting_date", "incident_date", "observation_date", "activity_date", "test_date")
    for field_name in date_fields:
        value = getattr(instance, field_name, None)
        if value and not period.start_date <= value <= period.end_date:
            raise ValidationError({field_name: f"Date must fall within {period}."})
    start = getattr(instance, "start_date", None)
    end = getattr(instance, "end_date", None)
    if start and end and end < start:
        raise ValidationError({"end_date": "End date cannot be before start date."})


@transaction.atomic
def save_entry(*, config, report, section_code, form, user):
    if not user_has_any_role(user, REPORT_AUTHOR_ROLE_CODES) or not reports_for_user(user).filter(pk=report.pk).exists():
        raise PermissionDenied("You cannot edit this village report.")
    locked_report = TNKReport.objects.select_for_update().get(pk=report.pk)
    if not locked_report.is_editable:
        raise ValidationError("This report is no longer editable.")
    instance = form.save(commit=False)
    bind_report_context(instance, locked_report, user)
    replaced = bool(instance.pk and supports_close_and_replace(instance))
    if replaced:
        changes = {name: form.cleaned_data[name] for name in config.fields if name in form.cleaned_data}
        instance = close_and_replace(current=instance, user=user, changes=changes)
        validate_entry_period(instance, locked_report)
    else:
        if instance.pk and hasattr(instance, "record_version"):
            instance.record_version += 1
        instance.full_clean()
        validate_entry_period(instance, locked_report)
        instance.save()
        form.save_m2m()
    section = ReportSectionStatus.objects.select_for_update().get(report=locked_report, section_code=section_code)
    if section.status == ReportSectionStatus.Status.NOT_STARTED:
        section.status = ReportSectionStatus.Status.IN_PROGRESS
    section.last_updated_by = user
    section.confirmed_unchanged = False
    section.save(update_fields=("status", "last_updated_by", "confirmed_unchanged", "last_updated_at"))
    from .progress import recalculate_report_progress
    recalculate_report_progress(locked_report)
    TNKReport.objects.filter(pk=locked_report.pk).update(record_version=F("record_version") + 1)
    record_event(actor=user, action="report.entry_saved", instance=instance, summary=f"Saved {config.label}", metadata={"report_uuid": str(report.uuid), "section_code": section_code, "entry_type": config.key})
    return instance
