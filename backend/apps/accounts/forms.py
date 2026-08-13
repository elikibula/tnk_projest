from django import forms
from django.db import models

from .models import UserLocationAssignment


class UserLocationAssignmentAdminForm(forms.ModelForm):
    class LocationLevel(models.TextChoices):
        PROVINCE = "province", "Province"
        TIKINA = "tikina", "Tikina"
        VILLAGE = "village", "Village"

    location_level = forms.ChoiceField(
        choices=LocationLevel.choices,
        help_text="Choose one access scope. Then select only the matching location below.",
    )

    class Meta:
        model = UserLocationAssignment
        fields = ("user", "location_level", "province", "tikina", "village", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial["location_level"] = next(
                (name for name in ("province", "tikina", "village") if getattr(self.instance, f"{name}_id")),
                None,
            )
        self.fields["province"].help_text = "Use only when Province is the chosen scope."
        self.fields["tikina"].help_text = "Use only when Tikina is the chosen scope."
        self.fields["village"].help_text = "Use only when Village is the chosen scope."

    def clean(self):
        cleaned = super().clean()
        level = cleaned.get("location_level")
        if level and not cleaned.get(level):
            self.add_error(level, f"Select a {self.fields[level].label.lower()} for this scope.")
        for field_name in ("province", "tikina", "village"):
            if field_name != level:
                cleaned[field_name] = None
                setattr(self.instance, field_name, None)
        return cleaned
