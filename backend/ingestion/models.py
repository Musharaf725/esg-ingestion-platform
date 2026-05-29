import uuid
from django.db import models

try:
    # Django's JSONField (works with SQLite since Django 3.1+)
    from django.db.models import JSONField
except Exception:
    JSONField = models.JSONField


class SourceType(models.TextChoices):
    SAP = "sap", "SAP"
    UTILITY = "utility", "Utility"
    TRAVEL = "travel", "Travel"


class UploadBatch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey("tenants.Organization", on_delete=models.CASCADE, related_name="upload_batches")
    source_type = models.CharField(max_length=32, choices=SourceType.choices)
    file_name = models.CharField(max_length=512)
    checksum = models.CharField(max_length=128, blank=True)
    created_by = models.ForeignKey("auth.User", null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "created_at"]),
            models.Index(fields=["source_type", "created_at"]),
        ]

    def __str__(self):
        return f"UploadBatch {self.id} ({self.source_type})"


class IngestionJob(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey("tenants.Organization", on_delete=models.CASCADE, related_name="ingestion_jobs")
    upload_batch = models.ForeignKey(
        UploadBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="jobs",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file_name = models.CharField(max_length=512)
    checksum = models.CharField(max_length=128, blank=True)
    source_type = models.CharField(max_length=32, choices=SourceType.choices)
    records_total = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    error_log = JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "uploaded_at"]),
            models.Index(fields=["source_type", "uploaded_at"]),
            models.Index(fields=["upload_batch", "uploaded_at"]),
        ]

    def __str__(self):
        return f"IngestionJob {self.id} ({self.file_name})"
