from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from apps.core.models import UUIDTimeStampedModel
from apps.core.validation import validate_non_negative, validate_subcounts

class PersonReference(UUIDTimeStampedModel):
    class Confidentiality(models.TextChoices):
        INTERNAL = "internal", "Internal"
        CONFIDENTIAL = "confidential", "Confidential"
        HIGHLY_RESTRICTED = "highly_restricted", "Highly restricted"
    full_name = models.CharField(max_length=200)
    gender = models.CharField(max_length=30, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)
    home_village = models.ForeignKey("locations.Village", on_delete=models.PROTECT, related_name="people")
    confidentiality_level = models.CharField(max_length=30, choices=Confidentiality.choices, default=Confidentiality.CONFIDENTIAL)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.full_name

class OfficialRole(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name_en = models.CharField(max_length=120)
    name_fj = models.CharField(max_length=120, blank=True)
    def __str__(self): return self.name_en

class OfficialAppointment(UUIDTimeStampedModel):
    person = models.ForeignKey(PersonReference, on_delete=models.PROTECT, related_name="appointments")
    village = models.ForeignKey("locations.Village", on_delete=models.PROTECT, related_name="official_appointments")
    role = models.ForeignKey(OfficialRole, on_delete=models.PROTECT)
    appointment_date = models.DateField()
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    confirmation_status = models.CharField(max_length=40, default="pending")
    appointment_reference = models.CharField(max_length=150, blank=True)
    is_current = models.BooleanField(default=True)
    change_reason = models.TextField(blank=True)
    supporting_document = models.FileField(upload_to="officials/%Y/%m/", null=True, blank=True)
    def clean(self):
        if self.effective_to and self.effective_to < self.effective_from: raise ValidationError({"effective_to": "End date cannot precede start date."})
        if self.is_current and self.effective_to: raise ValidationError({"is_current": "A current appointment cannot have an end date."})

class VillageCommittee(UUIDTimeStampedModel):
    TYPES = (("development","Development"),("health","Health"),("water","Water"),("natural_resources_disaster","Natural Resources and Disaster"),("education","Education"),("youth","Youth"),("women","Women"),("law_order","Law and Order"))
    village = models.ForeignKey("locations.Village", on_delete=models.PROTECT, related_name="committees")
    committee_type = models.CharField(max_length=40, choices=TYPES)
    name = models.CharField(max_length=160)
    formed_date = models.DateField(null=True, blank=True)
    dissolved_date = models.DateField(null=True, blank=True)
    mandate = models.TextField(blank=True)
    chairperson = models.ForeignKey(PersonReference, null=True, blank=True, on_delete=models.PROTECT, related_name="chaired_committees")
    secretary = models.ForeignKey(PersonReference, null=True, blank=True, on_delete=models.PROTECT, related_name="secretary_committees")
    constitution_available = models.BooleanField(null=True, blank=True)
    annual_plan_available = models.BooleanField(null=True, blank=True)
    bank_account_available = models.BooleanField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    def clean(self):
        if self.formed_date and self.dissolved_date and self.dissolved_date < self.formed_date:
            raise ValidationError({"dissolved_date": "Dissolution date cannot precede formation date."})
        if self.is_active and self.dissolved_date:
            raise ValidationError({"is_active": "A dissolved committee cannot remain active."})

class CommitteeMember(UUIDTimeStampedModel):
    committee = models.ForeignKey(VillageCommittee, on_delete=models.PROTECT, related_name="members")
    person = models.ForeignKey(PersonReference, on_delete=models.PROTECT, related_name="committee_memberships")
    position = models.CharField(max_length=100)
    gender = models.CharField(max_length=30, blank=True)
    age_group = models.ForeignKey("population.AgeGroup", null=True, blank=True, on_delete=models.PROTECT)
    joined_date = models.DateField()
    left_date = models.DateField(null=True, blank=True)
    training_received = models.BooleanField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    def clean(self):
        if self.left_date and self.left_date < self.joined_date:
            raise ValidationError({"left_date": "Leaving date cannot precede joining date."})
        if self.is_active and self.left_date:
            raise ValidationError({"is_active": "A member with a leaving date cannot remain active."})

class CommitteeMeeting(UUIDTimeStampedModel):
    committee = models.ForeignKey(VillageCommittee, on_delete=models.PROTECT, related_name="meetings")
    report = models.ForeignKey("reporting.TNKReport", on_delete=models.PROTECT, related_name="committee_meetings")
    meeting_date = models.DateField()
    chaired_by = models.ForeignKey(PersonReference, null=True, blank=True, on_delete=models.PROTECT)
    total_attendance = models.PositiveIntegerField()
    male_attendance = models.PositiveIntegerField(null=True, blank=True)
    female_attendance = models.PositiveIntegerField(null=True, blank=True)
    youth_attendance = models.PositiveIntegerField(null=True, blank=True)
    disability_attendance = models.PositiveIntegerField(null=True, blank=True)
    quorum_achieved = models.BooleanField(null=True, blank=True)
    minutes_available = models.BooleanField(null=True, blank=True)
    evidence_document = models.FileField(upload_to="meetings/%Y/%m/", null=True, blank=True)
    def clean(self):
        if self.committee_id and not self.committee.is_active:
            raise ValidationError({"committee": "Meetings cannot be added to an inactive committee."})
        known=sum(value or 0 for value in (self.male_attendance,self.female_attendance))
        if known>self.total_attendance: raise ValidationError({"total_attendance":"Male and female attendance cannot exceed total attendance."})
        validate_subcounts(self.total_attendance, youth_attendance=self.youth_attendance, disability_attendance=self.disability_attendance)

class MeetingDecision(UUIDTimeStampedModel):
    meeting = models.ForeignKey(CommitteeMeeting, on_delete=models.CASCADE, related_name="decisions")
    decision = models.TextField()
    responsible_person = models.CharField(max_length=200, blank=True)
    priority = models.CharField(max_length=20, default="medium")
    due_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, default="open")
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    reason_delayed = models.TextField(blank=True)
    evidence_document = models.FileField(upload_to="decisions/%Y/%m/", null=True, blank=True)
    def clean(self):
        if self.status.lower() == "completed" and not self.completion_date:
            raise ValidationError({"completion_date": "A completed decision requires a completion date."})
        if self.completion_date and self.meeting_id and self.completion_date < self.meeting.meeting_date:
            raise ValidationError({"completion_date": "Completion date cannot precede the meeting date."})

class VillageVisit(UUIDTimeStampedModel):
    village = models.ForeignKey("locations.Village", on_delete=models.PROTECT, related_name="visits")
    report = models.ForeignKey("reporting.TNKReport", on_delete=models.PROTECT, related_name="visits")
    visit_type = models.CharField(max_length=80)
    officer_name = models.CharField(max_length=200)
    organisation = models.CharField(max_length=160)
    visit_date = models.DateField()
    purpose = models.TextField()
    findings = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_due_date = models.DateField(null=True, blank=True)
    follow_up_status = models.CharField(max_length=30, blank=True)
    evidence_document = models.FileField(upload_to="visits/%Y/%m/", null=True, blank=True)

class TrainingActivity(UUIDTimeStampedModel):
    village = models.ForeignKey("locations.Village", on_delete=models.PROTECT, related_name="training_activities")
    report = models.ForeignKey("reporting.TNKReport", on_delete=models.PROTECT, related_name="training_activities")
    category = models.CharField(max_length=80)
    title = models.CharField(max_length=200)
    provider = models.CharField(max_length=160)
    start_date = models.DateField(); end_date = models.DateField()
    delivery_method = models.CharField(max_length=80, blank=True); target_group = models.CharField(max_length=120, blank=True)
    male_participants = models.PositiveIntegerField(null=True, blank=True); female_participants = models.PositiveIntegerField(null=True, blank=True)
    youth_participants = models.PositiveIntegerField(null=True, blank=True); participants_with_disability = models.PositiveIntegerField(null=True, blank=True); total_completed = models.PositiveIntegerField(null=True, blank=True)
    cost = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True); currency_code = models.CharField(max_length=3, default="FJD")
    funding_source = models.CharField(max_length=160, blank=True); expected_outcome = models.TextField(blank=True); actual_outcome = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False); follow_up_date = models.DateField(null=True, blank=True)
    evidence_document = models.FileField(upload_to="training/%Y/%m/", null=True, blank=True)
    def clean(self):
        if self.end_date < self.start_date: raise ValidationError({"end_date":"End date cannot precede start date."})
        total = (self.male_participants or 0) + (self.female_participants or 0)
        validate_subcounts(total, youth_participants=self.youth_participants, participants_with_disability=self.participants_with_disability, total_completed=self.total_completed)
        validate_non_negative(cost=self.cost)

class TrainingOutcomeReview(UUIDTimeStampedModel):
    training = models.ForeignKey(TrainingActivity, on_delete=models.CASCADE, related_name="outcome_reviews")
    review_date = models.DateField()
    participants_applying_skills = models.PositiveIntegerField(null=True, blank=True); projects_started = models.PositiveIntegerField(null=True, blank=True); businesses_started = models.PositiveIntegerField(null=True, blank=True)
    outcome_rating = models.CharField(max_length=30); challenges = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
