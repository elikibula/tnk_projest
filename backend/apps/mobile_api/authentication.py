from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone

from .models import MobileDevice


class ActiveDeviceJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        device_uuid = validated_token.get("device_uuid")
        if not device_uuid:
            raise AuthenticationFailed("This token is not bound to a registered device.", code="device_required")
        devices = MobileDevice.objects.filter(uuid=device_uuid, user=user, is_active=True, revoked_at__isnull=True)
        if not devices.exists():
            raise AuthenticationFailed("This mobile device has been revoked.", code="device_revoked")
        devices.update(last_seen_at=timezone.now())
        return user
