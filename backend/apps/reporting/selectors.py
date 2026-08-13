from django.db.models import QuerySet

from apps.accounts.selectors import villages_for_user
from .models import TNKReport


def reports_for_user(user) -> QuerySet[TNKReport]:
    return TNKReport.objects.filter(village__in=villages_for_user(user)).select_related(
        "village", "village__tikina", "reporting_period", "prepared_by", "previous_report"
    )
