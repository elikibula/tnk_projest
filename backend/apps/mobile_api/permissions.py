from rest_framework.permissions import BasePermission

from apps.core.security.confidentiality import can_view_report


class CanAccessReport(BasePermission):
    def has_object_permission(self, request, view, obj):
        return can_view_report(request.user, obj)
