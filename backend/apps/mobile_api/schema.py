from drf_spectacular.extensions import OpenApiAuthenticationExtension


class ActiveDeviceJWTScheme(OpenApiAuthenticationExtension):
    target_class = "apps.mobile_api.authentication.ActiveDeviceJWTAuthentication"
    name = "jwtAuth"

    def get_security_definition(self, auto_schema):
        return {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
