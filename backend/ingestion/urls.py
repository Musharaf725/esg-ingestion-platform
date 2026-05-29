from django.urls import path

from .views import IngestionJobListAPIView, IngestionUploadAPIView


urlpatterns = [
    path("upload/", IngestionUploadAPIView.as_view(), name="ingestion-upload"),
    path("jobs/", IngestionJobListAPIView.as_view(), name="ingestion-jobs-list"),
]
