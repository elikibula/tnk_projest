from django.core.exceptions import ValidationError


def validate_subcounts(total, **subcounts):
    """Reject demographic or category counts that exceed their parent total."""
    if total is None:
        return
    errors = {
        field: f"This count cannot exceed the total ({total})."
        for field, value in subcounts.items()
        if value is not None and value > total
    }
    if errors:
        raise ValidationError(errors)


def validate_non_negative(**values):
    errors = {
        field: "This value cannot be negative."
        for field, value in values.items()
        if value is not None and value < 0
    }
    if errors:
        raise ValidationError(errors)
