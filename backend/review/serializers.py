from rest_framework import serializers

from emissions.models import EmissionRecord, EmissionScope, RecordStatus, SourceType
from .models import AuditLog


class ApproveSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True, default="")


class RejectSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True, allow_blank=False)


class FlagSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True, allow_blank=False)
    note = serializers.CharField(required=False, allow_blank=True, default="")


class BulkApproveSerializer(serializers.Serializer):
    record_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=False)
    note = serializers.CharField(required=False, allow_blank=True, default="")


class ReviewRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmissionRecord
        fields = [
            "id",
            "organization",
            "upload_batch",
            "ingestion_job",
            "created_at",
            "updated_at",
            "amount",
            "unit",
            "period",
            "scope",
            "source_type",
            "source_ref",
            "raw_payload",
            "normalized_payload",
            "flag_reasons",
            "status",
            "normalization_version",
            "normalized_at",
            "normalization_notes",
            "reviewed_by",
            "reviewed_at",
            "rejection_reason",
        ]


class ReviewRecordQuerySerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=RecordStatus.choices, required=False)
    source_type = serializers.ChoiceField(choices=SourceType.choices, required=False)
    scope = serializers.ChoiceField(choices=EmissionScope.choices, required=False)
    suspicious_only = serializers.BooleanField(required=False, default=False)


class AuditLogSerializer(serializers.ModelSerializer):
    performed_by = serializers.StringRelatedField()

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "action",
            "old_value",
            "new_value",
            "performed_by",
            "timestamp",
            "note",
        ]
