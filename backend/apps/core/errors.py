from django.core.exceptions import ValidationError


def humanize_validation_error(error: ValidationError) -> str:
    """Turn Django's list/dictionary ValidationError representation into prose."""
    if hasattr(error, "message_dict"):
        parts = []
        for field, messages in error.message_dict.items():
            label = field.replace("_", " ").capitalize()
            parts.extend(f"{label}: {message}" for message in messages)
        return " ".join(parts)
    if hasattr(error, "messages"):
        return " ".join(str(message) for message in error.messages)
    return str(error).strip("[]'")
