from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import ValidationError
from django.db import transaction

from apps.accounts.models import Role, User, UserLocationAssignment, UserRoleAssignment
from apps.locations.models import Province, Tikina, Village
from apps.reporting.models import ReportingPeriod

from .permissions import is_system_administrator
from .selectors import locations_for_admin


ROLE_LEVELS = {
    Role.Codes.SYSTEM_ADMIN: None,
    Role.Codes.PROVINCIAL_ADMIN: "province",
    Role.Codes.ROKO_TUI: "province",
    Role.Codes.ROKO_VEIVUKE: "tikina",
    Role.Codes.MATA_NI_TIKINA: "tikina",
    Role.Codes.TURAGA_NI_KORO: "village",
    Role.Codes.VILLAGE_DATA_ASSISTANT: "village",
    Role.Codes.VILLAGE_NURSE: "village",
    Role.Codes.PROJECT_OFFICER: "province",
    Role.Codes.READ_ONLY_ANALYST: "province",
    Role.Codes.AUDITOR: "province",
}


class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class AdministrativeUserForm(StyledFormMixin, forms.ModelForm):
    role = forms.ModelChoiceField(queryset=Role.objects.none())
    province = forms.ModelChoiceField(queryset=Province.objects.none(), required=False)
    tikina = forms.ModelChoiceField(queryset=Tikina.objects.none(), required=False)
    village = forms.ModelChoiceField(queryset=Village.objects.none(), required=False)
    password1 = forms.CharField(widget=forms.PasswordInput, required=False, label="Temporary password")
    password2 = forms.CharField(widget=forms.PasswordInput, required=False, label="Confirm temporary password")

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "preferred_language", "is_active")

    def __init__(self, *args, actor, **kwargs):
        self.actor = actor
        super().__init__(*args, **kwargs)
        roles = Role.objects.filter(is_active=True)
        if not is_system_administrator(actor):
            roles = roles.exclude(code__in=(Role.Codes.SYSTEM_ADMIN, Role.Codes.PROVINCIAL_ADMIN))
        self.fields["role"].queryset = roles.order_by("name")
        provinces, tikina, villages = locations_for_admin(actor)
        self.fields["province"].queryset = provinces.filter(is_active=True)
        self.fields["tikina"].queryset = tikina.filter(is_active=True)
        self.fields["village"].queryset = villages.filter(is_active=True)
        if self.instance.pk:
            role_assignment = self.instance.role_assignments.filter(is_active=True).select_related("role").first()
            location = self.instance.location_assignments.filter(is_active=True).first()
            if role_assignment:
                self.initial["role"] = role_assignment.role
            if location:
                for field in ("province", "tikina", "village"):
                    value = getattr(location, field)
                    if value:
                        self.initial[field] = value
        else:
            self.fields["password1"].required = True
            self.fields["password2"].required = True

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get("role")
        password1, password2 = cleaned.get("password1"), cleaned.get("password2")
        if password1 or password2:
            if password1 != password2:
                self.add_error("password2", "The passwords do not match.")
            else:
                from django.contrib.auth.password_validation import validate_password

                try:
                    validate_password(password1, self.instance)
                except ValidationError as error:
                    self.add_error("password1", error)
        if not role:
            return cleaned
        if self.instance.pk and is_system_administrator(self.instance) and role.code != Role.Codes.SYSTEM_ADMIN:
            remaining = UserRoleAssignment.objects.filter(
                is_active=True, role__code=Role.Codes.SYSTEM_ADMIN, user__is_active=True
            ).exclude(user=self.instance).exists()
            if not remaining:
                self.add_error("role", "The last active System Administrator cannot be demoted.")
        required_level = ROLE_LEVELS.get(role.code)
        selected = {name: cleaned.get(name) for name in ("province", "tikina", "village")}
        if required_level and not selected[required_level]:
            self.add_error(required_level, f"This role requires a {required_level} assignment.")
        for name, value in selected.items():
            if name != required_level and value:
                self.add_error(name, f"This role must be assigned at {required_level or 'national'} level.")
        if selected["tikina"] and selected["province"] and selected["tikina"].province_id != selected["province"].pk:
            self.add_error("tikina", "The Tikina does not belong to the selected province.")
        if selected["village"] and selected["tikina"] and selected["village"].tikina_id != selected["tikina"].pk:
            self.add_error("village", "The village does not belong to the selected Tikina.")
        return cleaned

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get("password1"):
            user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            UserRoleAssignment.objects.filter(user=user, is_active=True).update(is_active=False)
            UserRoleAssignment.objects.update_or_create(user=user, role=self.cleaned_data["role"], defaults={"is_active": True})
            UserLocationAssignment.objects.filter(user=user, is_active=True).update(is_active=False)
            level = ROLE_LEVELS.get(self.cleaned_data["role"].code)
            if level:
                UserLocationAssignment.objects.create(user=user, **{level: self.cleaned_data[level]})
        return user


class AdministrativePasswordForm(StyledFormMixin, SetPasswordForm):
    pass


class ReportingPeriodForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ReportingPeriod
        fields = ("year", "quarter", "start_date", "end_date", "submission_due_date", "is_open", "is_locked")
        widgets = {"start_date": forms.DateInput(attrs={"type": "date"}), "end_date": forms.DateInput(attrs={"type": "date"}), "submission_due_date": forms.DateInput(attrs={"type": "date"})}


class ProvinceForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Province
        fields = ("code", "name_en", "name_fj", "is_active")


class TikinaForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Tikina
        fields = ("province", "code", "name_en", "name_fj", "is_active")

    def __init__(self, *args, actor, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["province"].queryset = locations_for_admin(actor)[0]


class VillageForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Village
        fields = ("tikina", "code", "name_en", "name_fj", "island_name", "postal_address", "contact_phone", "contact_email", "is_active")

    def __init__(self, *args, actor, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tikina"].queryset = locations_for_admin(actor)[1]
