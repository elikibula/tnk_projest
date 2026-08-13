from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class ReportSectionStatus(models.Model):
    class Section(models.TextChoices):
        VILLAGE_PROFILE = "village_profile", "Village profile"
        LEADERSHIP_GOVERNANCE = "leadership_governance", "Leadership and governance"
        VISITS_TRAINING = "visits_training", "Visits and training"
        POPULATION_HOUSEHOLDS = "population_households", "Population and households"
        HOUSING_ASSETS = "housing_assets", "Housing and village assets"
        WATER = "water", "Water"
        SANITATION_WASTE = "sanitation_waste", "Sanitation and waste"
        ENERGY = "energy", "Electricity and energy"
        HEALTH = "health", "Health"
        DISABILITY = "disability", "Disability"
        AGRICULTURE_FOOD = "agriculture_food", "Agriculture and food security"
        BUSINESS_FINANCE = "business_finance", "Business and village finance"
        IVDP_PROJECTS = "ivdp_projects", "IVDP projects"
        CLIMATE_DISASTER = "climate_disaster", "Climate and disaster preparedness"
        TRADITIONAL_CULTURE = "traditional_culture", "Traditional leadership and culture"
        EVIDENCE_DECLARATIONS = "evidence_declarations", "Evidence and declarations"
        VALIDATION_SUBMISSION = "validation_submission", "Validation and submission"

    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not started"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETE = "complete", "Complete"
        NEEDS_ATTENTION = "needs_attention", "Needs attention"
        VERIFIED = "verified", "Verified"

    report = models.ForeignKey("reporting.TNKReport", on_delete=models.CASCADE, related_name="section_statuses")
    section_code = models.CharField(max_length=40, choices=Section.choices)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.NOT_STARTED)
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(0), MaxValueValidator(100)])
    issue_count = models.PositiveIntegerField(default=0)
    confirmed_unchanged = models.BooleanField(default=False)
    last_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="updated_report_sections")
    last_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("pk",)
        constraints = [models.UniqueConstraint(fields=("report", "section_code"), name="unique_report_section")]

    def __str__(self):
        return f"{self.report}: {self.get_section_code_display()}"
