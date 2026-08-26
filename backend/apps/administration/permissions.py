from functools import wraps

from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied

from apps.accounts.models import Role
from apps.accounts.permissions import user_has_any_role

ADMIN_ROLE_CODES = {Role.Codes.SYSTEM_ADMIN, Role.Codes.PROVINCIAL_ADMIN}


def is_administration_user(user):
    return user_has_any_role(user, ADMIN_ROLE_CODES)


def is_system_administrator(user):
    return user_has_any_role(user, {Role.Codes.SYSTEM_ADMIN})


def administration_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login

            return redirect_to_login(request.get_full_path())
        if not is_administration_user(request.user):
            raise PermissionDenied("You do not have access to Administration.")
        return view(request, *args, **kwargs)

    return wrapped


class AdministrationRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not is_administration_user(request.user):
            raise PermissionDenied("You do not have access to Administration.")
        return super().dispatch(request, *args, **kwargs)

