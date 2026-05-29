from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import IngestionJob, UploadBatch, SourceType
from . import services
from .serializers import IngestionJobSerializer, IngestionUploadSerializer


class IngestionUploadAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = IngestionUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.tenant is None:
            return Response({"error": "valid X-Tenant header required"}, status=status.HTTP_400_BAD_REQUEST)

        f = serializer.validated_data["file"]
        source_type = serializer.validated_data["source_type"]

        user = request.user if request.user.is_authenticated else None

        batch = UploadBatch.objects.create(
            organization=request.tenant,
            source_type=source_type,
            file_name=f.name,
            created_by=user,
        )

        job = IngestionJob.objects.create(
            organization=request.tenant,
            upload_batch=batch,
            file_name=f.name,
            source_type=source_type,
        )

        # Run ingestion synchronously (no Celery)
        result = services.run_ingestion_job(job, f, request.tenant)
        job.refresh_from_db()

        payload = {
            **result,
            "ingestion_job_id": str(job.id),
            "error_log": job.error_log,
            "normalization_warnings": job.error_log.get("warnings", []) if isinstance(job.error_log, dict) else [],
        }

        return Response(payload, status=status.HTTP_200_OK)


class IngestionJobListAPIView(generics.ListAPIView):
    serializer_class = IngestionJobSerializer

    def list(self, request, *args, **kwargs):
        if request.tenant is None:
            return Response({"error": "valid X-Tenant header required"}, status=status.HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return IngestionJob.objects.filter(organization=self.request.tenant).order_by("-uploaded_at")[:50]
