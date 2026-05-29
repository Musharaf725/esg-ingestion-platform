import uuid
from decimal import Decimal
from django.db import models

try:
    from django.db.models import JSONField
except Exception:
    JSONField = models.JSONField


class RecordStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    PENDING_REVIEW = "pending_review", "Pending Review"
    APPROVED = "approved", "Approved"
    FAILED = "failed", "Failed"
    REJECTED = "rejected", "Rejected"


class SourceType(models.TextChoices):
    SAP = "sap", "SAP"
    UTILITY = "utility", "Utility"
    TRAVEL = "travel", "Travel"


class EmissionScope(models.TextChoices):
    SCOPE_1 = "scope_1", "Scope 1"
    SCOPE_2 = "scope_2", "Scope 2"
    SCOPE_3 = "scope_3", "Scope 3"


class EmissionRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey("tenants.Organization", on_delete=models.CASCADE, related_name="emission_records")
    upload_batch = models.ForeignKey(
        "ingestion.UploadBatch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="emission_records",
    )
    ingestion_job = models.ForeignKey(
        "ingestion.IngestionJob",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="emission_records",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    amount = models.DecimalField(max_digits=20, decimal_places=6, default=Decimal("0"))
    unit = models.CharField(max_length=50, default="kgCO2e")
    period = models.CharField(max_length=64)
    scope = models.CharField(max_length=16, choices=EmissionScope.choices)
    source_type = models.CharField(max_length=32, choices=SourceType.choices)
    source_ref = JSONField(default=dict, blank=True)
    raw_payload = JSONField(default=dict, blank=True)
    normalized_payload = JSONField(default=dict, blank=True)
    flag_reasons = JSONField(default=list, blank=True)
    status = models.CharField(max_length=32, choices=RecordStatus.choices, default=RecordStatus.PENDING)
    normalization_version = models.CharField(max_length=32, default="v1")
    normalized_at = models.DateTimeField(null=True, blank=True)
    normalization_notes = models.TextField(blank=True, default="")

    # review fields
    reviewed_by = models.ForeignKey("auth.User", null=True, blank=True, on_delete=models.SET_NULL)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "source_type"]),
            models.Index(fields=["organization", "scope"]),
            models.Index(fields=["ingestion_job", "status"]),
            models.Index(fields=["upload_batch", "created_at"]),
            models.Index(fields=["created_at"]),
        ]

    IMMUTABLE_FIELDS_WHEN_APPROVED = {
        "organization_id",
        "upload_batch_id",
        "ingestion_job_id",
        "amount",
        "unit",
        "period",
        "scope",
        "source_type",
        "source_ref",
        "raw_payload",
        "normalized_payload",
        "flag_reasons",
        "normalization_version",
        "normalized_at",
        "normalization_notes",
    }

    def _raise_if_approved_mutation(self):
        if not self.pk:
            return
        original = EmissionRecord.objects.filter(pk=self.pk).first()
        if not original or original.status != RecordStatus.APPROVED:
            return

        if self.status != RecordStatus.APPROVED:
            raise ValueError("Approved records are immutable and cannot change status")

        for field_name in self.IMMUTABLE_FIELDS_WHEN_APPROVED:
            if getattr(original, field_name) != getattr(self, field_name):
                raise ValueError(f"Approved records are immutable; cannot change '{field_name}'")

    def save(self, *args, **kwargs):
        self._raise_if_approved_mutation()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.status == RecordStatus.APPROVED:
            raise ValueError("Approved records are immutable and cannot be deleted")
        return super().delete(*args, **kwargs)


class UnitConversion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey("tenants.Organization", on_delete=models.CASCADE, related_name="unit_conversions")
    from_unit = models.CharField(max_length=50)
    to_unit = models.CharField(max_length=50)
    factor = models.DecimalField(max_digits=20, decimal_places=12)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "from_unit", "to_unit"]),
        ]

    def convert(self, amount):
        return amount * self.factor
