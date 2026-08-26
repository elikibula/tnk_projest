from django import forms
from django.forms import formset_factory
from django.utils import timezone

from .models import EvidenceDocument, RecordPhoto
from .validators import validate_evidence_file


class RecordPhotoForm(forms.Form):
    image = forms.ImageField(label="Photo", validators=[validate_evidence_file], widget=forms.ClearableFileInput(attrs={"accept": "image/jpeg,image/png"}))
    caption = forms.CharField(max_length=200, widget=forms.TextInput(attrs={"placeholder": "What does this photo show?"}))
    captured_at = forms.DateTimeField(label="Date and time taken", widget=forms.DateTimeInput(attrs={"type": "datetime-local"}), help_text="Enter the actual capture date and time in your local timezone.")
    stage = forms.ChoiceField(choices=RecordPhoto.STAGES, initial="observation")
    confidentiality_level = forms.ChoiceField(choices=EvidenceDocument.LEVELS, initial="restricted")
    latitude = forms.DecimalField(required=False, max_digits=9, decimal_places=6, min_value=-90, max_value=90)
    longitude = forms.DecimalField(required=False, max_digits=9, decimal_places=6, min_value=-180, max_value=180)
    location_accuracy_metres = forms.DecimalField(required=False, max_digits=9, decimal_places=2, min_value=0, widget=forms.HiddenInput)

    def clean_captured_at(self):
        value = self.cleaned_data["captured_at"]
        if value > timezone.now():
            raise forms.ValidationError("The capture date cannot be in the future.")
        return value

    def clean(self):
        values = super().clean()
        latitude, longitude = values.get("latitude"), values.get("longitude")
        if (latitude is None) != (longitude is None):
            raise forms.ValidationError("Provide both latitude and longitude, or leave both blank.")
        if values.get("location_accuracy_metres") is not None and latitude is None:
            raise forms.ValidationError("GPS accuracy requires coordinates.")
        return values


RecordPhotoFormSet = formset_factory(RecordPhotoForm, extra=0, max_num=10, validate_max=True, absolute_max=10, min_num=1, validate_min=True)
