from django.contrib.auth.signals import user_logged_in,user_logged_out,user_login_failed
from django.db.models.signals import post_delete,post_save
from django.dispatch import receiver
from .models import UserLocationAssignment,UserRoleAssignment
from apps.audit.models import AuditEvent
def request_metadata(request): return {"ip_address":request.META.get("REMOTE_ADDR") if request else None,"user_agent":request.META.get("HTTP_USER_AGENT","") if request else ""}
@receiver(user_logged_in)
def logged_in(sender,request,user,**kwargs): AuditEvent.objects.create(actor=user,action="auth.login",object_type="accounts.User",object_uuid=user.uuid,summary="Successful login",metadata=request_metadata(request))
@receiver(user_logged_out)
def logged_out(sender,request,user,**kwargs):
    if user: AuditEvent.objects.create(actor=user,action="auth.logout",object_type="accounts.User",object_uuid=user.uuid,summary="Logout",metadata=request_metadata(request))
@receiver(user_login_failed)
def login_failed(sender,credentials,request,**kwargs): AuditEvent.objects.create(action="auth.login_failed",object_type="accounts.User",summary="Failed login",metadata=request_metadata(request))


def assignment_event(instance, action):
    if getattr(instance, "_request_audit_recorded", False):
        return
    AuditEvent.objects.create(
        action=action,
        object_type=instance._meta.label,
        object_uuid=instance.uuid,
        summary=str(instance),
        metadata={"user_id": instance.user_id, "is_active": getattr(instance, "is_active", None)},
    )


@receiver(post_save, sender=UserRoleAssignment)
def role_assignment_saved(sender, instance, created, **kwargs):
    assignment_event(instance, "role_assignment.created" if created else "role_assignment.changed")


@receiver(post_delete, sender=UserRoleAssignment)
def role_assignment_deleted(sender, instance, **kwargs):
    assignment_event(instance, "role_assignment.deleted")


@receiver(post_save, sender=UserLocationAssignment)
def location_assignment_saved(sender, instance, created, **kwargs):
    assignment_event(instance, "location_assignment.created" if created else "location_assignment.changed")


@receiver(post_delete, sender=UserLocationAssignment)
def location_assignment_deleted(sender, instance, **kwargs):
    assignment_event(instance, "location_assignment.deleted")
