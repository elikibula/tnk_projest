from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin

from .selectors import reports_for_user
from apps.core.security import can_view_report


class ScopedReportMixin(LoginRequiredMixin):
    def get_report(self):
        report = reports_for_user(self.request.user).filter(uuid=self.kwargs["report_uuid"]).first()
        if report is None or not can_view_report(self.request.user, report):
            raise PermissionDenied("You do not have access to this report.")
        return report
