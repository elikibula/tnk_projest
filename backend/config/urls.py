from django.contrib import admin
from django.urls import include, path
from apps.accounts.views import ThrottledLoginView
from apps.core.views import healthcheck
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("api/v1/", include("apps.mobile_api.urls")),
    path("healthz/", healthcheck, name="healthcheck"),
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin.site.urls),
    path("accounts/login/", ThrottledLoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("reports/", include("apps.reporting.urls")),
    path("documents/", include("apps.documents.urls")),
    path("analytics/", include("apps.analytics.urls")),
    path("administration/", include("apps.administration.urls")),
    path("", include("apps.core.urls")),
]
