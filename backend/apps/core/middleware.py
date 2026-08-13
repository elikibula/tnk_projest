import logging
import uuid


request_logger = logging.getLogger("tnk.request")


class RequestContextMiddleware:
    """Attach a non-sensitive correlation ID and log failures without request data."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = uuid.uuid4().hex
        response = self.get_response(request)
        response["X-Request-ID"] = request.request_id
        if response.status_code >= 500:
            request_logger.error(
                "Server error response",
                extra={
                    "event": "http.server_error",
                    "request_id": request.request_id,
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                },
            )
        return response

    def process_exception(self, request, exception):
        request_logger.error(
            "Unhandled request exception",
            extra={
                "event": "http.exception",
                "request_id": getattr(request, "request_id", ""),
                "method": request.method,
                "path": request.path,
                "exception_type": type(exception).__name__,
            },
        )
        return None


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.conf import settings

        response = self.get_response(request)
        response.setdefault("Content-Security-Policy", settings.CONTENT_SECURITY_POLICY)
        response.setdefault("Permissions-Policy", "camera=(), geolocation=(), microphone=(), payment=(), usb=()")
        return response
