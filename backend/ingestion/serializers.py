from rest_framework import serializers

from .models import IngestionJob, SourceType


class IngestionUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    source_type = serializers.ChoiceField(choices=SourceType.choices)


class IngestionJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngestionJob
        fields = [
            "id",
            "file_name",
            "source_type",
            "records_total",
            "records_failed",
            "error_log",
            "uploaded_at",
            "updated_at",
        ]
