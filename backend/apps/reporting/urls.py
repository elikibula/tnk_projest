from django.urls import path

from . import views

app_name = "reporting"
urlpatterns = [
    path("", views.report_list, name="list"),
    path("new/", views.report_create, name="create"),
    path("<uuid:report_uuid>/", views.ReportDetailView.as_view(), name="detail"),
    path("<uuid:report_uuid>/declare/", views.final_declaration, name="declare"),
    path("<uuid:report_uuid>/evidence/upload/", views.evidence_upload, name="evidence_upload"),
    path("<uuid:report_uuid>/workflow/<slug:action>/", views.workflow_action, name="workflow_action"),
    path("<uuid:report_uuid>/validate/", views.validate_report_view, name="validate"),
    path("<uuid:report_uuid>/amendments/", views.amendment_list, name="amendment_list"),
    path("<uuid:report_uuid>/amendments/new/", views.amendment_create, name="amendment_create"),
    path("amendments/<uuid:amendment_uuid>/", views.amendment_detail, name="amendment_detail"),
    path("amendments/<uuid:amendment_uuid>/changes/new/", views.amendment_change_create, name="amendment_change_create"),
    path("amendments/<uuid:amendment_uuid>/<slug:action>/", views.amendment_action, name="amendment_action"),
    path("<uuid:report_uuid>/sections/<slug:section_code>/", views.SectionUpdateView.as_view(), name="section_update"),
    path("<uuid:report_uuid>/sections/<slug:section_code>/<slug:entry_key>/new/", views.section_entry_create, name="entry_create"),
    path("<uuid:report_uuid>/sections/<slug:section_code>/<slug:entry_key>/<str:object_id>/edit/", views.section_entry_edit, name="entry_edit"),
]
