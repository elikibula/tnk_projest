from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def mobile_api_exception_handler(exc, context):
    if isinstance(exc, DjangoPermissionDenied):
        return Response({"code": "permission_denied", "detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
    if isinstance(exc, DjangoValidationError):
        detail = exc.message_dict if hasattr(exc, "message_dict") else exc.messages
        return Response({"code": "validation_error", "detail": detail}, status=status.HTTP_400_BAD_REQUEST)
    response = exception_handler(exc, context)
    if response is not None and isinstance(response.data, dict) and "code" not in response.data:
        response.data = {"code": getattr(exc, "default_code", "api_error"), **response.data}
    return response
