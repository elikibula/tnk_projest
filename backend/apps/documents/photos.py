from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import F
from django.http import Http404
from django.shortcuts import get_object_or_404

from apps.accounts.permissions import REPORT_AUTHOR_ROLE_CODES, user_has_any_role
from apps.audit.services import record_event
from apps.core.security import can_view_entry, can_view_report
from apps.reporting.models import TNKReport
from apps.reporting.section_entries import entry_queryset, entry_summary
from apps.reporting.section_registry import get_entry_config
from apps.reporting.selectors import reports_for_user
from .models import EvidenceDocument, EvidenceLink, RecordPhoto


PHOTO_SECTIONS = frozenset({"agriculture_food", "ivdp_projects", "housing_assets", "water", "climate_disaster"})


def photo_context(user, report_uuid, section_code, entry_key, identifier, *, editing=False):
    report = get_object_or_404(reports_for_user(user), uuid=report_uuid)
    config = get_entry_config(section_code, entry_key)
    if section_code not in PHOTO_SECTIONS or config is None:
        raise Http404("Photo evidence is not enabled for this entry type.")
    if not can_view_report(user, report) or not can_view_entry(user, section_code, config.model, report.village):
        raise PermissionDenied("You cannot access this record's photos.")
    if editing and (not report.is_editable or not user_has_any_role(user, REPORT_AUTHOR_ROLE_CODES)):
        raise PermissionDenied("This report cannot accept photos.")
    identifier = str(identifier)
    if not report.is_editable and report.master_snapshot_captured_at:
        from apps.reporting.history import is_master_entry
        if is_master_entry(section_code, entry_key):
            snapshot = get_object_or_404(report.master_snapshots, section_code=section_code, entry_key=entry_key, source_identifier=identifier)
            return report, config, identifier, snapshot.summary
    lookup = "uuid" if any(field.name == "uuid" for field in config.model._meta.fields) else "pk"
    try:
        instance = get_object_or_404(entry_queryset(config, report), **{lookup: identifier})
    except (ValidationError, ValueError):
        raise Http404("Record not found.")
    return report, config, str(getattr(instance, "uuid", instance.pk)), entry_summary(config, instance)


def save_record_photos(*, user, report, section_code, entry_key, identifier, rows):
    # Storage is not transactional: remove only files created by this attempt if it fails.
    stored = []
    try:
        with transaction.atomic():
            locked = TNKReport.objects.select_for_update().get(pk=report.pk)
            photo_context(user, locked.uuid, section_code, entry_key, identifier, editing=True)
            for row in rows:
                upload = row["image"]
                document = EvidenceDocument(
                    title=row["caption"], description=row["caption"], document_type="photograph",
                    file=upload, original_filename=upload.name, file_size=upload.size,
                    mime_type=upload.content_type, checksum="pending", uploaded_by=user,
                    **{key: row.get(key) for key in ("captured_at", "confidentiality_level", "latitude", "longitude", "location_accuracy_metres")},
                )
                document.full_clean(exclude=("checksum",))
                try:
                    document.save()
                finally:
                    if document.file and document.file._committed:
                        stored.append((document.file.storage, document.file.name))
                RecordPhoto.objects.create(document=document, report=locked, section_code=section_code, entry_key=entry_key, record_identifier=identifier, stage=row["stage"])
                EvidenceLink.objects.create(document=document, content_type=ContentType.objects.get_for_model(locked), object_id=locked.pk)
                record_event(actor=user, action="document.uploaded", instance=document, summary="Uploaded record photo evidence", metadata={"report_uuid": str(locked.uuid), "section_code": section_code, "entry_key": entry_key, "record_identifier": identifier})
            TNKReport.objects.filter(pk=locked.pk).update(record_version=F("record_version") + 1)
    except Exception:
        for storage, name in stored:
            storage.delete(name)
        raise
