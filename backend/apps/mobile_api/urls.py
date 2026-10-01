from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .views import BootstrapView, DashboardSummaryView, DeviceLoginView, DeviceTokenRefreshView, LogoutView, MeView, ReportDeclarationView, ReportDetailView, ReportEvidenceView, ReportListCreateView, ReportValidationView, ReportWorkflowView, ReportingPeriodListView, SyncBatchView, SyncChangesView, VillageListView

app_name = "mobile_api"

from .exploration import AnalyticsOverviewView, LocationDirectoryView
from .photo_reports import PhotoReportDetailView, PhotoReportImageView, PhotoReportListView

urlpatterns = [
    path("analytics/", AnalyticsOverviewView.as_view(), name="analytics"),
    path("locations/", LocationDirectoryView.as_view(), name="location-directory"),
    path("photo-reports/", PhotoReportListView.as_view(), name="photo-reports"),
    path("photo-reports/<uuid:report_uuid>/", PhotoReportDetailView.as_view(), name="photo-report-detail"),
    path("photo-reports/images/<uuid:document_uuid>/", PhotoReportImageView.as_view(), name="photo-report-image"),
    path("auth/login/", DeviceLoginView.as_view(), name="login"),
    path("auth/refresh/", DeviceTokenRefreshView.as_view(), name="refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("dashboard/", DashboardSummaryView.as_view(), name="dashboard"),
    path("locations/villages/", VillageListView.as_view(), name="villages"),
    path("reporting-periods/", ReportingPeriodListView.as_view(), name="reporting-periods"),
    path("reports/", ReportListCreateView.as_view(), name="reports"),
    path("reports/<uuid:uuid>/", ReportDetailView.as_view(), name="report-detail"),
    path("reports/<uuid:report_uuid>/evidence/", ReportEvidenceView.as_view(), name="report-evidence"),
    path("reports/<uuid:report_uuid>/validation/", ReportValidationView.as_view(), name="report-validation"),
    path("reports/<uuid:report_uuid>/declaration/", ReportDeclarationView.as_view(), name="report-declaration"),
    path("reports/<uuid:report_uuid>/workflow/<str:action>/", ReportWorkflowView.as_view(), name="report-workflow"),
    path("sync/bootstrap/", BootstrapView.as_view(), name="bootstrap"),
    path("sync/changes/", SyncChangesView.as_view(), name="sync-changes"),
    path("sync/batch/", SyncBatchView.as_view(), name="sync-batch"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="mobile_api:schema"), name="docs"),
]
