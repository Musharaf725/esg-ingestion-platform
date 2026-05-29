from django.urls import path

from .views import (
    ReviewApproveAPIView,
    ReviewAuditTrailAPIView,
    ReviewBulkApproveAPIView,
    ReviewFlagAPIView,
    ReviewRejectAPIView,
    ReviewRecordListAPIView,
)


urlpatterns = [
    path("records/", ReviewRecordListAPIView.as_view(), name="review-record-list"),
    path("bulk-approve/", ReviewBulkApproveAPIView.as_view(), name="review-bulk-approve"),
    path("<uuid:record_id>/approve/", ReviewApproveAPIView.as_view(), name="review-approve"),
    path("<uuid:record_id>/reject/", ReviewRejectAPIView.as_view(), name="review-reject"),
    path("<uuid:record_id>/flag/", ReviewFlagAPIView.as_view(), name="review-flag"),
    path("records/<uuid:record_id>/audit/", ReviewAuditTrailAPIView.as_view(), name="review-audit-trail"),
    path("records/<uuid:record_id>/approve/", ReviewApproveAPIView.as_view(), name="review-approve"),
    path("records/<uuid:record_id>/reject/", ReviewRejectAPIView.as_view(), name="review-reject"),
    path("records/<uuid:record_id>/flag/", ReviewFlagAPIView.as_view(), name="review-flag"),
]
