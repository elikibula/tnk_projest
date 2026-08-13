from apps.core.historical import close_and_replace

from .models import Household


def replace_household(*, current: Household, user, **changes):
    return close_and_replace(current=current, user=user, changes=changes)
