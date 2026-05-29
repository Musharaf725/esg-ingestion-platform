from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from emissions.models import EmissionRecord
from .serializers import (
    AuditLogSerializer,
    BulkApproveSerializer,
    ApproveSerializer,
    FlagSerializer,
    RejectSerializer,
    ReviewRecordQuerySerializer,
    ReviewRecordSerializer,
)
from .models import AuditLog


class ReviewRecordPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ReviewRecordListAPIView(generics.ListAPIView):
    serializer_class = ReviewRecordSerializer
    pagination_class = ReviewRecordPagination

    def list(self, request, *args, **kwargs):
        if request.tenant is None:
            return Response({"error": "valid X-Tenant header required"}, status=status.HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = EmissionRecord.objects.select_related(
            "organization",
            "ingestion_job",
            "upload_batch",
            "reviewed_by",
        ).order_by("-created_at")

        queryset = queryset.filter(organization=self.request.tenant)

        query_serializer = ReviewRecordQuerySerializer(data=self.request.query_params)
        query_serializer.is_valid(raise_exception=True)
        filters = query_serializer.validated_data

        if filters.get("status"):
            queryset = queryset.filter(status=filters["status"])
        if filters.get("source_type"):
            queryset = queryset.filter(source_type=filters["source_type"])
        if filters.get("scope"):
            queryset = queryset.filter(scope=filters["scope"])
        if filters.get("suspicious_only"):
            queryset = queryset.exclude(flag_reasons=[])

        return queryset


class ReviewAuditTrailAPIView(generics.ListAPIView):
    serializer_class = AuditLogSerializer

    def list(self, request, *args, **kwargs):
        if request.tenant is None:
            return Response({"error": "valid X-Tenant header required"}, status=status.HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        record_id = self.kwargs["record_id"]
        return AuditLog.objects.filter(organization=self.request.tenant, record_id=record_id).order_by("-timestamp")


def _get_record_for_tenant(request, record_id):
    if request.tenant is None:
        return None, Response({"error": "valid X-Tenant header required"}, status=status.HTTP_400_BAD_REQUEST)
    record = get_object_or_404(EmissionRecord, pk=record_id, organization=request.tenant)
    return record, None


class ReviewApproveAPIView(APIView):
    def post(self, request, record_id):
        serializer = ApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        record, error_response = _get_record_for_tenant(request, record_id)
        if error_response:
            return error_response

        user = request.user if request.user.is_authenticated else None
        note = serializer.validated_data.get("note", "")

        try:
            services.approve_record(record, user, note)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": "approved"}, status=status.HTTP_200_OK)


class ReviewRejectAPIView(APIView):
    def post(self, request, record_id):
        serializer = RejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        record, error_response = _get_record_for_tenant(request, record_id)
        if error_response:
            return error_response

        user = request.user if request.user.is_authenticated else None
        reason = serializer.validated_data["reason"]

        try:
            services.reject_record(record, user, reason)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": "rejected"}, status=status.HTTP_200_OK)


class ReviewFlagAPIView(APIView):
    def post(self, request, record_id):
        serializer = FlagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        record, error_response = _get_record_for_tenant(request, record_id)
        if error_response:
            return error_response

        user = request.user if request.user.is_authenticated else None
        reason = serializer.validated_data["reason"]
        note = serializer.validated_data.get("note", "")

        try:
            services.flag_record(record, user, reason=reason, note=note)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": record.status, "flagged": True}, status=status.HTTP_200_OK)


class ReviewBulkApproveAPIView(APIView):
    def post(self, request):
        if request.tenant is None:
            return Response({"error": "valid X-Tenant header required"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BulkApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record_ids = list(dict.fromkeys(serializer.validated_data["record_ids"]))
        note = serializer.validated_data.get("note", "")

        records = list(
            EmissionRecord.objects.filter(organization=request.tenant, pk__in=record_ids).select_related("organization")
        )

        if len(records) != len(record_ids):
            found_ids = {record.id for record in records}
            missing = [str(record_id) for record_id in record_ids if record_id not in found_ids]
            return Response({"error": "some records were not found", "missing": missing}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user if request.user.is_authenticated else None
        result = services.bulk_approve_records(records, user, note=note)

        payload = {
            "status": "completed",
            "approved_count": result["count"],
            "errors": result["errors"],
        }
        return Response(payload, status=status.HTTP_200_OK)
