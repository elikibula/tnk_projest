from enum import IntEnum
from functools import lru_cache

from apps.accounts.models import Role
from apps.accounts.selectors import villages_for_user


class ConfidentialityLevel(IntEnum):
    PUBLIC = 0
    INTERNAL = 1
    RESTRICTED = 2
    HIGHLY_RESTRICTED = 3


LEVEL_ALIASES = {
    "public": ConfidentialityLevel.PUBLIC,
    "internal": ConfidentialityLevel.INTERNAL,
    "confidential": ConfidentialityLevel.RESTRICTED,
    "restricted": ConfidentialityLevel.RESTRICTED,
    "highly_restricted": ConfidentialityLevel.HIGHLY_RESTRICTED,
}

ALL_SECTIONS = frozenset(
    {
        "village_profile",
        "leadership_governance",
        "visits_training",
        "population_households",
        "housing_assets",
        "water",
        "sanitation_waste",
        "energy",
        "health",
        "disability",
        "agriculture_food",
        "business_finance",
        "ivdp_projects",
        "climate_disaster",
        "traditional_culture",
        "evidence_declarations",
        "validation_submission",
    }
)

FULL_REPORT_ROLES = frozenset(
    {
        Role.Codes.SYSTEM_ADMIN,
        Role.Codes.PROVINCIAL_ADMIN,
        Role.Codes.ROKO_TUI,
        Role.Codes.ROKO_VEIVUKE,
        Role.Codes.MATA_NI_TIKINA,
        Role.Codes.TURAGA_NI_KORO,
        Role.Codes.VILLAGE_DATA_ASSISTANT,
        Role.Codes.AUDITOR,
    }
)

SECTION_ACCESS = {
    Role.Codes.SYSTEM_ADMIN: ALL_SECTIONS,
    Role.Codes.PROVINCIAL_ADMIN: ALL_SECTIONS,
    Role.Codes.ROKO_TUI: ALL_SECTIONS,
    Role.Codes.ROKO_VEIVUKE: ALL_SECTIONS,
    Role.Codes.MATA_NI_TIKINA: ALL_SECTIONS,
    Role.Codes.TURAGA_NI_KORO: ALL_SECTIONS,
    Role.Codes.VILLAGE_DATA_ASSISTANT: ALL_SECTIONS,
    Role.Codes.AUDITOR: ALL_SECTIONS,
    Role.Codes.VILLAGE_NURSE: frozenset({"village_profile", "health", "disability"}),
    Role.Codes.PROJECT_OFFICER: frozenset({"village_profile", "ivdp_projects"}),
    Role.Codes.READ_ONLY_ANALYST: frozenset(),
}

ROLE_CLEARANCE = {
    Role.Codes.SYSTEM_ADMIN: ConfidentialityLevel.HIGHLY_RESTRICTED,
    Role.Codes.PROVINCIAL_ADMIN: ConfidentialityLevel.HIGHLY_RESTRICTED,
    Role.Codes.ROKO_TUI: ConfidentialityLevel.HIGHLY_RESTRICTED,
    Role.Codes.ROKO_VEIVUKE: ConfidentialityLevel.HIGHLY_RESTRICTED,
    Role.Codes.MATA_NI_TIKINA: ConfidentialityLevel.HIGHLY_RESTRICTED,
    Role.Codes.TURAGA_NI_KORO: ConfidentialityLevel.HIGHLY_RESTRICTED,
    Role.Codes.VILLAGE_DATA_ASSISTANT: ConfidentialityLevel.HIGHLY_RESTRICTED,
    Role.Codes.VILLAGE_NURSE: ConfidentialityLevel.HIGHLY_RESTRICTED,
    Role.Codes.AUDITOR: ConfidentialityLevel.HIGHLY_RESTRICTED,
    Role.Codes.PROJECT_OFFICER: ConfidentialityLevel.RESTRICTED,
    Role.Codes.READ_ONLY_ANALYST: ConfidentialityLevel.INTERNAL,
}

ANALYTICS_ROLES = frozenset(SECTION_ACCESS)
REPORT_EVIDENCE_ROLES = FULL_REPORT_ROLES
PRE_SUBMISSION_EVIDENCE_ROLES = frozenset(
    {
        Role.Codes.SYSTEM_ADMIN,
        Role.Codes.PROVINCIAL_ADMIN,
        Role.Codes.TURAGA_NI_KORO,
        Role.Codes.VILLAGE_DATA_ASSISTANT,
    }
)
PRE_SUBMISSION_STATUSES = frozenset({"draft", "returned_to_village", "ready_for_validation"})

HIGHLY_RESTRICTED_MODELS = frozenset(
    {
        "wellbeing.HealthConditionSnapshot",
        "wellbeing.VillageHealthAccessSnapshot",
        "wellbeing.DisabilitySnapshot",
        "wellbeing.CommunitySafetyIncident",
    }
)

RESTRICTED_MODELS = frozenset(
    {
        "governance.PersonReference",
        "governance.CommitteeMember",
        "population.Household",
        "economy.VillageFinancialAccount",
        "economy.VillageFinancialSnapshot",
    }
)


def role_codes_for_user(user):
    if not getattr(user, "is_authenticated", False):
        return set()
    if user.is_superuser:
        return {Role.Codes.SYSTEM_ADMIN}
    return set(
        user.role_assignments.filter(is_active=True, role__is_active=True).values_list(
            "role__code", flat=True
        )
    )


def permitted_section_codes(user):
    if not getattr(user, "is_authenticated", False):
        return frozenset()
    if user.is_superuser:
        return ALL_SECTIONS
    allowed = set()
    for code in role_codes_for_user(user):
        allowed.update(SECTION_ACCESS.get(code, ()))
    return frozenset(allowed)


def can_view_section(user, section_code):
    return section_code in permitted_section_codes(user)


def can_view_analytics(user):
    return bool(role_codes_for_user(user) & ANALYTICS_ROLES)


def can_export_report_summary(user):
    return can_view_analytics(user)


def _clearance(user):
    if getattr(user, "is_superuser", False):
        return ConfidentialityLevel.HIGHLY_RESTRICTED
    return max(
        (ROLE_CLEARANCE.get(code, ConfidentialityLevel.PUBLIC) for code in role_codes_for_user(user)),
        default=ConfidentialityLevel.PUBLIC,
    )


def _level(value):
    return LEVEL_ALIASES.get(str(value or "internal").lower(), ConfidentialityLevel.RESTRICTED)


def record_confidentiality_level(record):
    explicit = getattr(record, "confidentiality_level", None)
    if explicit is not None:
        return _level(explicit)
    label = record if isinstance(record, str) else record._meta.label
    if label in HIGHLY_RESTRICTED_MODELS:
        return ConfidentialityLevel.HIGHLY_RESTRICTED
    if label in RESTRICTED_MODELS:
        return ConfidentialityLevel.RESTRICTED
    return ConfidentialityLevel.INTERNAL


@lru_cache(maxsize=1)
def _model_sections():
    from apps.reporting.section_registry import SECTION_ENTRIES

    result = {}
    for section_code, configs in SECTION_ENTRIES.items():
        for config in configs:
            result.setdefault(config.model._meta.label, section_code)
    return result


def section_for_record(record):
    if hasattr(record, "section_code"):
        return record.section_code
    label = record if isinstance(record, str) else record._meta.label
    return _model_sections().get(label)


def village_for_record(record):
    direct = getattr(record, "village", None) or getattr(record, "home_village", None)
    if direct is not None:
        return direct
    for attribute in (
        "report",
        "original_report",
        "amendment",
        "committee",
        "meeting",
        "account",
        "water_source",
        "facility",
        "project",
        "traditional_unit",
        "title",
        "training",
    ):
        parent = getattr(record, attribute, None)
        if parent is not None and parent is not record:
            village = village_for_record(parent)
            if village is not None:
                return village
    return None


def _in_location_scope(user, record):
    village = village_for_record(record)
    return village is not None and villages_for_user(user).filter(pk=village.pk).exists()


def can_view_report(user, report):
    if not getattr(user, "is_authenticated", False):
        return False
    if not permitted_section_codes(user):
        return False
    return _in_location_scope(user, report)


def can_view_entry(user, section_code, model, village):
    if not can_view_section(user, section_code):
        return False
    if not villages_for_user(user).filter(pk=village.pk).exists():
        return False
    label = model if isinstance(model, str) else model._meta.label
    if _clearance(user) < record_confidentiality_level(label):
        return False
    if label == "wellbeing.CommunitySafetyIncident":
        return bool(role_codes_for_user(user) & FULL_REPORT_ROLES)
    return True


def can_view_record(user, record):
    if not getattr(user, "is_authenticated", False):
        return False
    section_code = section_for_record(record)
    village = village_for_record(record)
    if village is None:
        return False
    if section_code:
        return can_view_entry(user, section_code, record, village)
    return _in_location_scope(user, record) and _clearance(user) >= record_confidentiality_level(record)


def can_view_health_detail(user, village):
    return can_view_entry(user, "health", "wellbeing.HealthConditionSnapshot", village)


def can_view_household_detail(user, village):
    return can_view_entry(user, "population_households", "population.Household", village)


def can_view_safety_detail(user, village):
    return can_view_entry(user, "health", "wellbeing.CommunitySafetyIncident", village)


def can_view_document(user, document):
    if not getattr(user, "is_authenticated", False):
        return False
    if _clearance(user) < record_confidentiality_level(document):
        return False
    roles = role_codes_for_user(user)
    # Record photos must satisfy both report workflow and entry permissions.
    # A report-level EvidenceLink must not bypass the record's section scope.
    photo = getattr(document, "record_photo", None)
    if photo is not None:
        from apps.reporting.section_registry import get_entry_config
        config = get_entry_config(photo.section_code, photo.entry_key)
        report = photo.report
        allowed_roles = PRE_SUBMISSION_EVIDENCE_ROLES if report.status in PRE_SUBMISSION_STATUSES else REPORT_EVIDENCE_ROLES
        return bool(config and roles & allowed_roles and can_view_report(user, report)
                    and can_view_entry(user, photo.section_code, config.model, report.village))
    for link in document.links.select_related("content_type"):
        linked = link.content_object
        if linked is None:
            continue
        if linked._meta.label == "reporting.TNKReport":
            allowed_roles = PRE_SUBMISSION_EVIDENCE_ROLES if linked.status in PRE_SUBMISSION_STATUSES else REPORT_EVIDENCE_ROLES
            if roles & allowed_roles and can_view_report(user, linked):
                return True
        elif can_view_record(user, linked):
            return True
    return False


def can_export_record(user, record):
    if not can_view_record(user, record):
        return False
    if record_confidentiality_level(record) == ConfidentialityLevel.HIGHLY_RESTRICTED:
        return False
    return bool(role_codes_for_user(user) & {Role.Codes.SYSTEM_ADMIN, Role.Codes.PROVINCIAL_ADMIN, Role.Codes.AUDITOR})
