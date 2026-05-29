import uuid
from django.db import models

try:
    from django.db.models import JSONField
except Exception:
    JSONField = models.JSONField


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey("tenants.Organization", on_delete=models.CASCADE, related_name="audit_logs")
    record = models.ForeignKey("emissions.EmissionRecord", on_delete=models.CASCADE, related_name="audit_logs")
    action = models.CharField(max_length=64)
    old_value = JSONField(default=dict, blank=True)
    new_value = JSONField(default=dict, blank=True)
    performed_by = models.ForeignKey("auth.User", null=True, blank=True, on_delete=models.SET_NULL)
    note = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "timestamp"]),
            models.Index(fields=["record", "timestamp"]),
            models.Index(fields=["action", "timestamp"]),
        ]

    def __str__(self):
        return f"AuditLog {self.action} on {self.record_id}"

    def save(self, *args, **kwargs):
        if self.pk and AuditLog.objects.filter(pk=self.pk).exists():
            raise ValueError("AuditLog entries are immutable")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("AuditLog entries are immutable")
