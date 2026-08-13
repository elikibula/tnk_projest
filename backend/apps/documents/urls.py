from django.urls import path
from .views import download
app_name="documents"; urlpatterns=[path("<uuid:document_uuid>/download/",download,name="download")]
