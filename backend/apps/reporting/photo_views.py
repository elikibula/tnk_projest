from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import redirect, render

from apps.accounts.permissions import REPORT_AUTHOR_ROLE_CODES, user_has_any_role
from apps.core.security import can_view_document
from apps.documents.models import RecordPhoto
from apps.documents.photo_forms import RecordPhotoFormSet
from apps.documents.photos import photo_context, save_record_photos


@login_required
def record_photos(request, report_uuid, section_code, entry_key, object_id):
    report, config, identifier, summary = photo_context(request.user, report_uuid, section_code, entry_key, object_id, editing=request.method == "POST")
    can_edit = report.is_editable and user_has_any_role(request.user, REPORT_AUTHOR_ROLE_CODES)
    formset = RecordPhotoFormSet(request.POST if request.method == "POST" else None, request.FILES if request.method == "POST" else None)
    if request.method == "POST" and formset.is_valid():
        try:
            save_record_photos(user=request.user, report=report, section_code=section_code, entry_key=entry_key, identifier=identifier, rows=[form.cleaned_data for form in formset if form.cleaned_data])
        except (ValidationError, PermissionDenied) as error:
            formset._non_form_errors = formset.error_class([str(error)])
        else:
            messages.success(request, "Photo evidence saved. Verification and completion status are unchanged.")
            return redirect("reporting:record_photos", report_uuid=report.uuid, section_code=section_code, entry_key=entry_key, object_id=identifier)
    photos = [photo for photo in RecordPhoto.objects.filter(report=report, section_code=section_code, entry_key=entry_key, record_identifier=identifier).select_related("document").order_by("document__captured_at", "pk") if can_view_document(request.user, photo.document)]
    response = render(request, "reporting/record_photos.html", {"report": report, "section_code": section_code, "config": config, "summary": summary, "photos": photos, "formset": formset, "can_edit": can_edit})
    response["Permissions-Policy"] = "camera=(), geolocation=(self), microphone=(), payment=(), usb=()"
    response["Cache-Control"] = "private, no-store"
    return response
