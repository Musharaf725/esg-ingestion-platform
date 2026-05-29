from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/ingestion/", include("ingestion.urls")),
    path("api/review/", include("review.urls")),
]