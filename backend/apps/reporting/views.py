import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .amendments import (
    ADMIN_EDIT_ROLES,
    APPROVE_ROLES,
    OFFICIAL_STATUSES,
    REQUEST_ROLES,
    add_amendment_change,
    authoritative_amendment,
    authoritative_changes,
    create_amendment,
    transition_amendment,
)
from .forms import (
    AmendmentChangeForm,
    AmendmentCreateForm,
    EvidenceUploadForm,
    ReportCreateForm,
    SectionStatusForm,
    build_entry_form,
)
from .mixins import ScopedReportMixin
from .models import ReportAmendment, ReportSectionStatus
from .selectors import reports_for_user
from .services import create_report, update_section_status
from apps.workflow.models import FinalDeclaration
from apps.workflow.services import transition_report
from apps.workflow.services import available_actions
from apps.data_quality.services import validate_report
from .section_entries import entry_queryset, entry_rows, save_entry
from .section_registry import SECTION_ENTRIES, get_entry_config, section_data_types
from apps.accounts.permissions import REPORT_AUTHOR_ROLE_CODES, user_has_any_role
from apps.core.security import can_view_document, can_view_entry, can_view_report, can_view_section, permitted_section_codes
from apps.documents.models import EvidenceDocument, EvidenceLink
from apps.audit.services import record_event
from apps.core.errors import humanize_validation_error


workflow_logger = logging.getLogger("tnk.workflow")
validation_logger = logging.getLogger("tnk.validation")
from django.contrib.contenttypes.models import ContentType


@login_required
def report_list(request):
    if not permitted_section_codes(request.user):
        raise PermissionDenied("Your role can access aggregated analytics, not detailed report records.")
    return render(request, "reporting/report_list.html", {"reports": reports_for_user(request.user), "can_create": user_has_any_role(request.user, REPORT_AUTHOR_ROLE_CODES)})


@login_required
def report_create(request):
    if not user_has_any_role(request.user, REPORT_AUTHOR_ROLE_CODES):
        raise PermissionDenied("Your role cannot create TNK reports.")
    form = ReportCreateForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        try:
            report = create_report(prepared_by=request.user, **form.cleaned_data)
        except (PermissionDenied, ValidationError) as error:
            form.add_error(None, error)
        else:
            messages.success(request, "TNK report created with all reporting sections.")
            return redirect("reporting:detail", report_uuid=report.uuid)
    return render(request, "reporting/report_form.html", {"form": form})


class ReportDetailView(ScopedReportMixin, View):
    def get(self, request, report_uuid):
        report = self.get_report()
        allowed_sections = permitted_section_codes(request.user)
        sections = list(report.section_statuses.filter(section_code__in=allowed_sections).select_related("last_updated_by"))
        for section in sections:
            section.data_types = section_data_types(section.section_code)
        return render(request, "reporting/report_detail.html", {
            "report": report,
            "sections": sections,
            "workflow_actions": available_actions(report, request.user),
            "quality_issues": report.quality_issues.filter(resolved=False, section__in=allowed_sections).select_related("rule")[:50],
            "can_validate": report.is_editable and user_has_any_role(request.user, REPORT_AUTHOR_ROLE_CODES),
            "amendments": report.amendments.select_related("requested_by", "approved_by"),
            "authoritative_amendment": authoritative_amendment(report),
            "can_request_amendment": report.status in OFFICIAL_STATUSES and user_has_any_role(request.user, REQUEST_ROLES),
        })


class SectionUpdateView(ScopedReportMixin, View):
    def get_section(self, report):
        return get_object_or_404(report.section_statuses, section_code=self.kwargs["section_code"])

    def get(self, request, report_uuid, section_code):
        report = self.get_report()
        section = self.get_section(report)
        if not can_view_section(request.user, section_code):
            raise PermissionDenied("Your role cannot access this report section.")
        configs = [config for config in SECTION_ENTRIES.get(section_code, ()) if can_view_entry(request.user, section_code, config.model, report.village)]
        entry_groups = [(config, entry_rows(config, report), entry_rows(config, report.previous_report) if report.previous_report else []) for config in configs]
        can_edit = report.is_editable and user_has_any_role(request.user, REPORT_AUTHOR_ROLE_CODES)
        evidence_documents = [document for document in EvidenceDocument.objects.filter(links__content_type=ContentType.objects.get_for_model(report), links__object_id=report.pk) if can_view_document(request.user, document)] if section_code == ReportSectionStatus.Section.EVIDENCE_DECLARATIONS else EvidenceDocument.objects.none()
        return render(request, "reporting/section_form.html", {"report": report, "section": section, "form": SectionStatusForm(instance=section, initial={"expected_version": report.record_version}), "entry_groups": entry_groups, "can_edit": can_edit, "evidence_documents": evidence_documents, "authoritative_changes": authoritative_changes(report, section_code=section_code)})

    def post(self, request, report_uuid, section_code):
        report = self.get_report()
        section = self.get_section(report)
        if not can_view_section(request.user, section_code):
            raise PermissionDenied("Your role cannot access this report section.")
        form = SectionStatusForm(request.POST, instance=section)
        if form.is_valid():
            try:
                update_section_status(report=report, section_code=section.section_code, user=request.user, **form.cleaned_data)
            except (PermissionDenied, ValidationError) as error:
                form.add_error(None, error)
            else:
                messages.success(request, "Section progress saved.")
                return redirect("reporting:detail", report_uuid=report.uuid)
        configs = [config for config in SECTION_ENTRIES.get(section_code, ()) if can_view_entry(request.user, section_code, config.model, report.village)]
        entry_groups = [(config, entry_rows(config, report), entry_rows(config, report.previous_report) if report.previous_report else []) for config in configs]
        can_edit = report.is_editable and user_has_any_role(request.user, REPORT_AUTHOR_ROLE_CODES)
        return render(request, "reporting/section_form.html", {"report": report, "section": section, "form": form, "entry_groups": entry_groups, "can_edit": can_edit})


def entry_context(report_uuid, section_code, entry_key, user):
    report = get_object_or_404(reports_for_user(user), uuid=report_uuid)
    if not can_view_report(user, report):
        raise PermissionDenied("You do not have access to this report.")
    section = get_object_or_404(report.section_statuses, section_code=section_code)
    config = get_entry_config(section_code, entry_key)
    if config is None:
        raise PermissionDenied("This entry type does not belong to the selected section.")
    if not can_view_entry(user, section_code, config.model, report.village):
        raise PermissionDenied("Your role cannot access this data-entry type.")
    if not report.is_editable or not user_has_any_role(user, REPORT_AUTHOR_ROLE_CODES):
        raise PermissionDenied("This report is read-only for your role or status.")
    return report, section, config


@login_required
def section_entry_create(request, report_uuid, section_code, entry_key):
    report, section, config = entry_context(report_uuid, section_code, entry_key, request.user)
    if not config.allow_create:
        raise PermissionDenied("This master record can only be edited.")
    form = build_entry_form(config, report=report, data=request.POST or None, files=request.FILES or None)
    if request.method == "POST" and form.is_valid():
        try:
            save_entry(config=config, report=report, section_code=section_code, form=form, user=request.user)
        except (PermissionDenied, ValidationError) as error:
            form.add_error(None, error)
        else:
            messages.success(request, f"{config.label} saved.")
            return redirect("reporting:section_update", report_uuid=report.uuid, section_code=section_code)
    return render(request, "reporting/entry_form.html", {"report": report, "section": section, "config": config, "form": form, "editing": False})


@login_required
def section_entry_edit(request, report_uuid, section_code, entry_key, object_id):
    report, section, config = entry_context(report_uuid, section_code, entry_key, request.user)
    lookup = {"uuid": object_id} if any(field.name == "uuid" for field in config.model._meta.fields) else {"pk": object_id}
    instance = get_object_or_404(entry_queryset(config, report), **lookup)
    form = build_entry_form(config, report=report, data=request.POST or None, files=request.FILES or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        try:
            save_entry(config=config, report=report, section_code=section_code, form=form, user=request.user)
        except (PermissionDenied, ValidationError) as error:
            form.add_error(None, error)
        else:
            messages.success(request, f"{config.label} updated.")
            return redirect("reporting:section_update", report_uuid=report.uuid, section_code=section_code)
    return render(request, "reporting/entry_form.html", {"report": report, "section": section, "config": config, "form": form, "editing": True})


@login_required
def evidence_upload(request, report_uuid):
    report = get_object_or_404(reports_for_user(request.user), uuid=report_uuid)
    if not report.is_editable or not user_has_any_role(request.user, REPORT_AUTHOR_ROLE_CODES):
        raise PermissionDenied("This report cannot accept evidence.")
    form = EvidenceUploadForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        document = form.save(commit=False)
        document.uploaded_by = request.user
        from pathlib import Path
        document.original_filename = Path(document.file.name).name
        document.mime_type = getattr(document.file, "content_type", "application/octet-stream")
        document.file_size = document.file.size
        document.checksum = "pending"
        document.full_clean(exclude=("checksum",))
        document.save()
        EvidenceLink.objects.create(document=document, content_type=ContentType.objects.get_for_model(report), object_id=report.pk)
        section = report.section_statuses.get(section_code=ReportSectionStatus.Section.EVIDENCE_DECLARATIONS)
        if section.status == ReportSectionStatus.Status.NOT_STARTED:
            section.status = ReportSectionStatus.Status.IN_PROGRESS
        section.last_updated_by = request.user
        section.save()
        from .progress import recalculate_report_progress
        recalculate_report_progress(report)
        record_event(actor=request.user, action="document.uploaded", instance=document, summary=f"Uploaded evidence for {report}")
        messages.success(request, "Evidence uploaded securely.")
        return redirect("reporting:section_update", report_uuid=report.uuid, section_code=ReportSectionStatus.Section.EVIDENCE_DECLARATIONS)
    return render(request, "reporting/evidence_form.html", {"report": report, "form": form})


@login_required
def final_declaration(request, report_uuid):
    report = get_object_or_404(reports_for_user(request.user), uuid=report_uuid)
    if request.method != "POST" or not report.is_editable or not user_has_any_role(request.user, REPORT_AUTHOR_ROLE_CODES):
        raise PermissionDenied("This declaration cannot be changed.")
    FinalDeclaration.objects.update_or_create(report=report, defaults={"declared_by": request.user, "declaration_text": "I declare this report complete and accurate to the best of my knowledge.", "acknowledged": request.POST.get("acknowledged") == "on"})
    from .progress import recalculate_report_progress
    recalculate_report_progress(report)
    messages.success(request, "Final declaration saved.")
    return redirect("reporting:detail", report_uuid=report.uuid)


@login_required
def workflow_action(request, report_uuid, action):
    if request.method != "POST":
        raise PermissionDenied("Workflow actions require confirmation.")
    report = get_object_or_404(reports_for_user(request.user), uuid=report_uuid)
    try:
        transition_report(report=report, user=request.user, action=action, comment=request.POST.get("comment", ""), acknowledged=request.POST.get("acknowledged") == "on", ip_address=request.META.get("REMOTE_ADDR"), user_agent=request.META.get("HTTP_USER_AGENT", ""))
    except (PermissionDenied, ValidationError) as error:
        workflow_logger.warning(
            "Workflow action rejected",
            extra={"event": "workflow.rejected", "action": action, "request_id": getattr(request, "request_id", "")},
        )
        messages.error(request, humanize_validation_error(error) if isinstance(error, ValidationError) else str(error))
    else:
        messages.success(request, f"Workflow action '{action}' completed.")
    return redirect("reporting:detail", report_uuid=report.uuid)


@login_required
def validate_report_view(request, report_uuid):
    if request.method != "POST":
        raise PermissionDenied("Validation requires confirmation.")
    report = get_object_or_404(reports_for_user(request.user), uuid=report_uuid)
    if not report.is_editable or not user_has_any_role(request.user, REPORT_AUTHOR_ROLE_CODES):
        raise PermissionDenied("Only an assigned report author can validate an editable report.")
    issues = validate_report(report)
    if issues.exists():
        validation_logger.warning(
            "Report validation found unresolved issues",
            extra={"event": "validation.issues", "request_id": getattr(request, "request_id", "")},
        )
        messages.warning(request, f"Validation found {issues.count()} issue(s). Review them before submission.")
    else:
        messages.success(request, "Validation passed with no unresolved issues.")
    return redirect("reporting:detail", report_uuid=report.uuid)


def _scoped_amendment(user, amendment_uuid):
    reports = reports_for_user(user)
    amendment = get_object_or_404(
        ReportAmendment.objects.select_related(
            "original_report__village__tikina__province",
            "original_report__reporting_period",
            "requested_by",
            "approved_by",
            "rejected_by",
        ),
        uuid=amendment_uuid,
        original_report__in=reports,
    )
    if not can_view_report(user, amendment.original_report):
        raise PermissionDenied("You do not have access to this report amendment.")
    return amendment


@login_required
def amendment_list(request, report_uuid):
    report = get_object_or_404(reports_for_user(request.user), uuid=report_uuid)
    if not can_view_report(request.user, report):
        raise PermissionDenied("You do not have access to this report.")
    return render(
        request,
        "reporting/amendment_list.html",
        {
            "report": report,
            "amendments": report.amendments.select_related("requested_by", "approved_by"),
            "can_request": report.status in OFFICIAL_STATUSES and user_has_any_role(request.user, REQUEST_ROLES),
        },
    )


@login_required
def amendment_create(request, report_uuid):
    report = get_object_or_404(reports_for_user(request.user), uuid=report_uuid)
    form = AmendmentCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            amendment = create_amendment(report=report, user=request.user, **form.cleaned_data)
        except (PermissionDenied, ValidationError) as error:
            form.add_error(None, error)
        else:
            messages.success(request, "Amendment request created. Add each corrected field before submitting it for review.")
            return redirect("reporting:amendment_detail", amendment_uuid=amendment.uuid)
    return render(request, "reporting/amendment_form.html", {"report": report, "form": form})


@login_required
def amendment_detail(request, amendment_uuid):
    amendment = _scoped_amendment(request.user, amendment_uuid)
    return render(
        request,
        "reporting/amendment_detail.html",
        {
            "amendment": amendment,
            "report": amendment.original_report,
            "changes": amendment.changes.select_related("indicator", "created_by"),
            "is_requester": amendment.requested_by_id == request.user.pk,
            "can_edit_amendment": amendment.status == ReportAmendment.Status.DRAFT and (
                amendment.requested_by_id == request.user.pk or user_has_any_role(request.user, ADMIN_EDIT_ROLES)
            ),
            "can_review_amendment": amendment.status == ReportAmendment.Status.SUBMITTED
            and amendment.requested_by_id != request.user.pk
            and user_has_any_role(request.user, APPROVE_ROLES),
        },
    )


@login_required
def amendment_change_create(request, amendment_uuid):
    amendment = _scoped_amendment(request.user, amendment_uuid)
    form = AmendmentChangeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            add_amendment_change(amendment=amendment, user=request.user, **form.cleaned_data)
        except (PermissionDenied, ValidationError) as error:
            form.add_error(None, error)
        else:
            messages.success(request, "Correction added. The approved report itself has not been changed.")
            return redirect("reporting:amendment_detail", amendment_uuid=amendment.uuid)
    return render(request, "reporting/amendment_change_form.html", {"amendment": amendment, "report": amendment.original_report, "form": form})


@login_required
def amendment_action(request, amendment_uuid, action):
    if request.method != "POST":
        raise PermissionDenied("Amendment workflow actions require confirmation.")
    amendment = _scoped_amendment(request.user, amendment_uuid)
    try:
        transition_amendment(
            amendment=amendment,
            user=request.user,
            action=action,
            comment=request.POST.get("comment", ""),
            acknowledged=request.POST.get("acknowledged") == "on",
        )
    except (PermissionDenied, ValidationError) as error:
        messages.error(request, humanize_validation_error(error) if isinstance(error, ValidationError) else str(error))
    else:
        messages.success(request, f"Amendment {action} completed.")
    return redirect("reporting:amendment_detail", amendment_uuid=amendment.uuid)
