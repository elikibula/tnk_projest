import json

from django import forms
from django.forms import modelform_factory
from apps.documents.models import EvidenceDocument
from .itaukei import localize_form
from .form_choices import controlled_choices

from apps.accounts.permissions import REPORT_AUTHOR_ROLE_CODES, user_has_any_role
from apps.accounts.selectors import villages_for_user
from .models import ReportingPeriod, ReportSectionStatus


class ReportCreateForm(forms.Form):
    village = forms.ModelChoiceField(queryset=None)
    reporting_period = forms.ModelChoiceField(queryset=ReportingPeriod.objects.none())

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        can_author = user_has_any_role(user, REPORT_AUTHOR_ROLE_CODES)
        self.fields["village"].queryset = villages_for_user(user).filter(is_active=True) if can_author else villages_for_user(user).none()
        self.fields["reporting_period"].queryset = ReportingPeriod.objects.filter(is_open=True, is_locked=False) if can_author else ReportingPeriod.objects.none()
        localize_form(self)


class SectionStatusForm(forms.ModelForm):
    expected_version = forms.IntegerField(widget=forms.HiddenInput)

    class Meta:
        model = ReportSectionStatus
        fields = ("status", "confirmed_unchanged")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = [
            choice for choice in self.fields["status"].choices
            if choice[0] in {
                ReportSectionStatus.Status.NOT_STARTED,
                ReportSectionStatus.Status.IN_PROGRESS,
                ReportSectionStatus.Status.COMPLETE,
                ReportSectionStatus.Status.NEEDS_ATTENTION,
            }
        ]
        localize_form(self)


def build_entry_form(config, *, report, data=None, files=None, instance=None):
    form_class = modelform_factory(config.model, fields=config.fields)
    form = form_class(data=data, files=files, instance=instance)
    village = report.village
    relation_paths = {
        "person": ("home_village", village),
        "chairperson": ("home_village", village),
        "secretary": ("home_village", village),
        "chaired_by": ("home_village", village),
        "owner_person": ("home_village", village),
        "committee": ("village", village),
        "meeting": ("report", report),
        "water_source": ("village", village),
        "facility": ("village", village),
        "account": ("village", village),
        "project": ("village", village),
        "milestone": ("project__village", village),
        "traditional_unit": ("village", village),
    }
    for field_name, (lookup, value) in relation_paths.items():
        if field_name in form.fields and hasattr(form.fields[field_name], "queryset"):
            form.fields[field_name].queryset = form.fields[field_name].queryset.filter(**{lookup: value})
    for field_name, field in form.fields.items():
        choices = controlled_choices(config.model, field_name)
        if choices and not isinstance(field, forms.ModelChoiceField):
            current_value = getattr(instance, field_name, None) if instance is not None else None
            choices = list(choices)
            if current_value not in (None, "") and current_value not in {value for value, _label in choices}:
                choices.append((current_value, f"Previously entered: {current_value}"))
            form.fields[field_name] = forms.ChoiceField(
                label=field.label,
                required=field.required,
                help_text=field.help_text,
                choices=(("", "Select an option") , *choices) if not field.required else choices,
            )
            field = form.fields[field_name]
        if field_name.endswith("count") or field_name in {"count", "quantity", "households_served", "people_served"}:
            field.help_text = "Use 0 only for a confirmed none. Leave blank when the value was not answered."
        elif field_name == "verification_status":
            field.help_text = "Village users submit this for verification; an authorised reviewer records final verification."
            field.choices = [(value, label) for value, label in field.choices if value != "verified"]
        elif field_name == "confidence_level":
            field.help_text = "Rate confidence based on the source and collection method."
        elif field_name == "source_reference":
            field.help_text = "Enter the register, document, interview or reference used."
    for field in form.fields.values():
        css = "w-full rounded border border-slate-300 p-2 focus:border-teal-700 focus:ring-teal-700"
        field.widget.attrs["class"] = css
        if isinstance(field.widget, forms.CheckboxInput):
            field.widget.attrs["class"] = "h-5 w-5 rounded border-slate-300 text-teal-700"
        if isinstance(field.widget, forms.DateInput):
            field.widget.input_type = "date"
        if isinstance(field.widget, forms.DateTimeInput):
            field.widget.input_type = "datetime-local"
    return localize_form(form)


class EvidenceUploadForm(forms.ModelForm):
    class Meta:
        model = EvidenceDocument
        fields = ("title", "document_type", "file", "description", "confidentiality_level")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["document_type"] = forms.ChoiceField(
            label=self.fields["document_type"].label,
            choices=controlled_choices(EvidenceDocument, "document_type"),
        )
        localize_form(self)


class AmendmentCreateForm(forms.Form):
    reason = forms.CharField(
        label="Why is this amendment needed?",
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="Explain the error, its impact, and how it was discovered.",
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Optional supporting context for the reviewer.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        localize_form(self)


class AmendmentChangeForm(forms.Form):
    section_code = forms.ChoiceField(label="Report section", choices=ReportSectionStatus.Section.choices)
    entry_key = forms.CharField(
        label="Entry type",
        help_text="Use the entry key shown beside the record on the report section page.",
    )
    source_identifier = forms.CharField(
        label="Record identifier",
        help_text="Enter the record UUID or number shown beside the record.",
    )
    field_name = forms.CharField(
        label="Field name",
        help_text="Enter the field name to correct, for example household_count.",
    )
    amended_value = forms.CharField(
        label="Corrected value",
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text="The original value is retrieved from the approved report and cannot be supplied by the requester.",
    )
    change_reason = forms.CharField(
        label="Reason for this correction",
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    indicator_code = forms.CharField(
        required=False,
        label="Affected indicator code",
        help_text="Optional. Use only when this correction changes a calculated indicator.",
    )
    amended_indicator_value = forms.DecimalField(required=False, max_digits=18, decimal_places=4)
    amended_indicator_numerator = forms.DecimalField(required=False, max_digits=18, decimal_places=4)
    amended_indicator_denominator = forms.DecimalField(required=False, max_digits=18, decimal_places=4)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        localize_form(self)

    def clean_amended_value(self):
        raw = self.cleaned_data["amended_value"].strip()
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return raw
