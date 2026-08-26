from django.urls import path
from .views import download, photo_preview
app_name="documents"; urlpatterns=[path("<uuid:document_uuid>/download/",download,name="download"), path("<uuid:document_uuid>/preview/",photo_preview,name="photo_preview")]
