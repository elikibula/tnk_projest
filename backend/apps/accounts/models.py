import uuid
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

class User(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    preferred_language = models.CharField(max_length=5, choices=(("en", "English"), ("fj", "iTaukei")), default="en")
    record_version = models.PositiveIntegerField(default=1)

class Role(models.Model):
    class Codes(models.TextChoices):
        SYSTEM_ADMIN = "system_admin", "System Administrator"
        PROVINCIAL_ADMIN = "provincial_admin", "Provincial Administrator"
        ROKO_TUI = "roko_tui", "Roko Tui"
        ROKO_VEIVUKE = "roko_veivuke", "Roko Veivuke"
        MATA_NI_TIKINA = "mata_ni_tikina", "Mata ni Tikina"
        TURAGA_NI_KORO = "turaga_ni_koro", "Turaga ni Koro"
        VILLAGE_DATA_ASSISTANT = "village_data_assistant", "Village Data Assistant"
        VILLAGE_NURSE = "village_nurse", "Village Nurse"
        PROJECT_OFFICER = "project_officer", "Project Officer"
        READ_ONLY_ANALYST = "read_only_analyst", "Read-only Analyst"
        AUDITOR = "auditor", "Auditor"
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    code = models.CharField(max_length=40, choices=Codes.choices, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name

class UserRoleAssignment(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="role_assignments")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="user_assignments")
    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=("user", "role"), name="unique_user_role")]

    def __str__(self):
        user_name = self.user.get_full_name().strip() or self.user.username
        return f"{user_name} — {self.role.name}"

class UserLocationAssignment(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="location_assignments")
    province = models.ForeignKey("locations.Province", null=True, blank=True, on_delete=models.CASCADE)
    tikina = models.ForeignKey("locations.Tikina", null=True, blank=True, on_delete=models.CASCADE)
    village = models.ForeignKey("locations.Village", null=True, blank=True, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    def clean(self):
        if sum(value is not None for value in (self.province, self.tikina, self.village)) != 1:
            raise ValidationError("Select exactly one location level.")
    def __str__(self):
        user_name = self.user.get_full_name().strip() or self.user.username
        location = self.village or self.tikina or self.province
        return f"{user_name} — {location}"
    class Meta:
        constraints = [models.CheckConstraint(condition=(models.Q(province__isnull=False, tikina__isnull=True, village__isnull=True) | models.Q(province__isnull=True, tikina__isnull=False, village__isnull=True) | models.Q(province__isnull=True, tikina__isnull=True, village__isnull=False)), name="exactly_one_location_level")]
