from django.urls import path
from . import views

app_name = "analytics"
urlpatterns = [
    path("", views.dashboard, name="dashboard"), path("national/", views.national, name="national"),
    path("province/<uuid:location_uuid>/", views.province, name="province"), path("tikina/<uuid:location_uuid>/", views.tikina, name="tikina"), path("village/<uuid:location_uuid>/", views.village, name="village"),
    path("compare/", views.compare, name="compare"), path("reporting/", views.reporting, name="reporting"), path("data-quality/", views.data_quality, name="data_quality"), path("search/", views.search_locations, name="search"),
    path("exports/summary.csv", views.export_summary, name="summary_export"), path("exports/<str:format>/", views.export_reports, name="export"),
]
