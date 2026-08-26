from django.urls import path

from . import views

app_name = "administration"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("users/", views.user_list, name="user_list"),
    path("users/create/", views.user_create, name="user_create"),
    path("users/<uuid:user_uuid>/", views.user_detail, name="user_detail"),
    path("users/<uuid:user_uuid>/edit/", views.user_edit, name="user_edit"),
    path("users/<uuid:user_uuid>/status/", views.user_toggle_active, name="user_toggle_active"),
    path("users/<uuid:user_uuid>/password/", views.user_password, name="user_password"),
    path("reporting-periods/", views.period_list, name="period_list"),
    path("reporting-periods/create/", views.period_form, name="period_create"),
    path("reporting-periods/<uuid:period_uuid>/edit/", views.period_form, name="period_edit"),
    path("reporting-periods/<uuid:period_uuid>/<str:action>/", views.period_toggle, name="period_toggle"),
    path("locations/", views.location_index, name="location_list"),
    path("locations/<str:location_type>/create/", views.location_form, name="location_create"),
    path("locations/<str:location_type>/<uuid:location_uuid>/edit/", views.location_form, name="location_edit"),
    path("location-options/", views.location_options, name="location_options"),
    path("audit/", views.audit_list, name="audit_list"),
]
