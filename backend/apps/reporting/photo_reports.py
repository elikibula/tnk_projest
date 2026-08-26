"""Read-only, senior-officer views of existing protected evidence."""
from pathlib import Path

from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_GET

from apps.accounts.permissions import PHOTO_REPORT_ROLE_CODES, user_has_any_role
from apps.accounts.selectors import villages_for_user
from apps.core.security import can_view_document, can_view_report
from apps.core.security.confidentiality import PRE_SUBMISSION_EVIDENCE_ROLES, PRE_SUBMISSION_STATUSES
from apps.documents.models import EvidenceDocument, RecordPhoto
from apps.documents.photos import PHOTO_SECTIONS
from apps.locations.models import Province, Tikina
from .models import ReportSectionStatus
from .section_registry import get_entry_config
from .selectors import reports_for_user


class PhotoReportFilters(forms.Form):
    province = forms.ModelChoiceField(queryset=Province.objects.none(), required=False, empty_label="All provinces")
    tikina = forms.ModelChoiceField(queryset=Tikina.objects.none(), required=False, empty_label="All tikina")
    village = forms.ModelChoiceField(queryset=None, required=False, empty_label="All villages")
    year = forms.TypedChoiceField(coerce=int, required=False, empty_value=None)
    quarter = forms.TypedChoiceField(coerce=int, required=False, empty_value=None, choices=[("", "All quarters"), (1, "Q1"), (2, "Q2"), (3, "Q3"), (4, "Q4")])

    def __init__(self, *args, user, reports, **kwargs):
        super().__init__(*args, **kwargs)
        villages = villages_for_user(user)
        self.fields["village"].queryset = villages
        self.fields["tikina"].queryset = Tikina.objects.filter(pk__in=villages.values("tikina_id"))
        self.fields["province"].queryset = Province.objects.filter(pk__in=villages.values("tikina__province_id"))
        years = reports.order_by("-reporting_period__year").values_list("reporting_period__year", flat=True).distinct()
        self.fields["year"].choices = [("", "All years"), *((year, year) for year in years)]


class GalleryFilters(forms.Form):
    area = forms.ChoiceField(required=False, choices=[("", "All areas"), *((code, label) for code, label in ReportSectionStatus.Section.choices if code in PHOTO_SECTIONS), ("general", "General report evidence")])
    stage = forms.ChoiceField(required=False, choices=[("", "All stages"), *RecordPhoto.STAGES, ("unspecified", "Not specified")])


def _require_senior(user):
    if not user_has_any_role(user, PHOTO_REPORT_ROLE_CODES):
        raise PermissionDenied("Photo Reports is available to Roko Tui Veivuke and higher roles.")


def _private_render(request, template, context):
    response = render(request, template, context)
    response["Cache-Control"] = "private, no-store"
    return response


def _page_context(request, items, size):
    page = Paginator(items, size).get_page(request.GET.get("page"))
    query = request.GET.copy()
    query.pop("page", None)
    return {"page_obj": page, "page_query": query.urlencode()}


@login_required
@require_GET
def photo_report_list(request):
    _require_senior(request.user)
    reports = reports_for_user(request.user).select_related("village__tikina__province")
    form = PhotoReportFilters(request.GET, user=request.user, reports=reports)
    if form.is_valid():
        for field, lookup in {"province": "village__tikina__province", "tikina": "village__tikina", "village": "village", "year": "reporting_period__year", "quarter": "reporting_period__quarter"}.items():
            if form.cleaned_data[field]:
                reports = reports.filter(**{lookup: form.cleaned_data[field]})
    else:
        reports = reports.none()
    reports = reports.order_by("-reporting_period__year", "-reporting_period__quarter", "village__name_en", "pk")
    return _private_render(request, "reporting/photo_report_list.html", {"filters": form, **_page_context(request, reports, 20)})


@login_required
@require_GET
def photo_report_detail(request, report_uuid):
    _require_senior(request.user)
    report = get_object_or_404(reports_for_user(request.user), uuid=report_uuid)
    if not can_view_report(request.user, report):
        raise PermissionDenied("You cannot view this report.")
    documents = EvidenceDocument.objects.filter(
        links__content_type=ContentType.objects.get_for_model(report), links__object_id=report.pk,
    ).select_related("record_photo", "record_photo__report", "record_photo__report__village").prefetch_related("links__content_type").order_by("captured_at", "uploaded_at", "pk").distinct()
    if report.status in PRE_SUBMISSION_STATUSES and not user_has_any_role(request.user, PRE_SUBMISSION_EVIDENCE_ROLES):
        documents = documents.none()
    rows = []
    section_labels = dict(ReportSectionStatus.Section.choices)
    for document in documents:
        if Path(document.file.name).suffix.lower() not in {".jpg", ".jpeg", ".png"} or not can_view_document(request.user, document):
            continue
        photo = getattr(document, "record_photo", None)
        if photo and photo.report_id != report.pk:
            continue
        area = photo.section_code if photo else "general"
        config = get_entry_config(photo.section_code, photo.entry_key) if photo else None
        record_url = (reverse("reporting:section_update", args=(report.uuid, photo.section_code)) + f"#record-{photo.entry_key}-{photo.record_identifier}") if config else reverse("reporting:section_update", args=(report.uuid, "evidence_declarations"))
        rows.append({"document": document, "area": area, "area_label": section_labels.get(area, "General report evidence"), "stage": photo.stage if photo else "unspecified", "stage_label": photo.get_stage_display() if photo else "Not specified", "record_label": config.display_label if config else "Report evidence", "record_identifier": photo.record_identifier if photo else "", "record_url": record_url})
    total = len(rows)
    form = GalleryFilters(request.GET)
    if form.is_valid():
        rows = [row for row in rows if (not form.cleaned_data["area"] or row["area"] == form.cleaned_data["area"]) and (not form.cleaned_data["stage"] or row["stage"] == form.cleaned_data["stage"])]
    else:
        rows = []
    order = {"before": 0, "progress": 1, "after": 2, "observation": 3, "unspecified": 4}
    rows.sort(key=lambda row: order.get(row["stage"], 4))
    return _private_render(request, "reporting/photo_report_detail.html", {"report": report, "filters": form, "total_photos": total, "filtered_photos": len(rows), **_page_context(request, rows, 24)})
