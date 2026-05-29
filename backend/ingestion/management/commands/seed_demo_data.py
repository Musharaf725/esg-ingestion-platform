from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from emissions.models import EmissionRecord, EmissionScope, RecordStatus, SourceType
from ingestion.models import IngestionJob, UploadBatch, SourceType as IngestionSourceType
from tenants.models import Organization, TenantUser


class Command(BaseCommand):
    help = "Seed a demo organization, tenant user, upload batch, ingestion job, and sample ESG records."

    def add_arguments(self, parser):
        parser.add_argument("--organization", default="demo-org")
        parser.add_argument("--username", default="demo-user")
        parser.add_argument("--email", default="demo@example.com")
        parser.add_argument("--password", default="demo-pass123")

    @transaction.atomic
    def handle(self, *args, **options):
        organization_name = options["organization"]
        username = options["username"]
        email = options["email"]
        password = options["password"]

        organization, _ = Organization.objects.get_or_create(name=organization_name)

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={"email": email},
        )
        if created:
            user.set_password(password)
            user.save(update_fields=["password"])

        TenantUser.objects.get_or_create(user=user, defaults={"organization": organization})

        batch, _ = UploadBatch.objects.get_or_create(
            organization=organization,
            source_type=IngestionSourceType.SAP,
            file_name="demo-sap.csv",
            defaults={"created_by": user},
        )

        job, _ = IngestionJob.objects.get_or_create(
            organization=organization,
            upload_batch=batch,
            file_name="demo-sap.csv",
            source_type=IngestionSourceType.SAP,
            defaults={"checksum": "demo-checksum"},
        )

        record, record_created = EmissionRecord.objects.get_or_create(
            organization=organization,
            upload_batch=batch,
            ingestion_job=job,
            source_type=SourceType.SAP,
            period="2026-05",
            defaults={
                "amount": Decimal("12.500000"),
                "unit": "kgCO2e",
                "scope": EmissionScope.SCOPE_1,
                "source_ref": {"source": "demo", "row": 1},
                "raw_payload": {"CO2e_kg": "12.5", "unit": "kgCO2e", "scope": "1"},
                "normalized_payload": {
                    "amount": "12.500000",
                    "unit": "kgCO2e",
                    "period": "2026-05",
                    "scope": "scope_1",
                },
                "flag_reasons": ["demo seed record"],
                "status": RecordStatus.PENDING_REVIEW,
                "normalization_version": "v1",
                "normalization_notes": "Seeded demo record for review flow",
            },
        )

        self.stdout.write(self.style.SUCCESS(f"Seeded organization: {organization.name}"))
        self.stdout.write(self.style.SUCCESS(f"Seeded user: {user.username} (created={created})"))
        self.stdout.write(self.style.SUCCESS(f"Seeded upload batch: {batch.id}"))
        self.stdout.write(self.style.SUCCESS(f"Seeded ingestion job: {job.id}"))
        self.stdout.write(self.style.SUCCESS(f"Seeded emission record: {record.id} (created={record_created})"))
