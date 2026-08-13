import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("mobile_api", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="MobileSyncSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("uploaded_count", models.PositiveIntegerField(default=0)),
                ("downloaded_count", models.PositiveIntegerField(default=0)),
                ("conflict_count", models.PositiveIntegerField(default=0)),
                ("failed_count", models.PositiveIntegerField(default=0)),
                ("status", models.CharField(choices=[("running", "Running"), ("completed", "Completed"), ("partial", "Partial"), ("failed", "Failed")], default="running", max_length=20)),
                ("device", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="mobile_api.mobiledevice")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="MobileChangeLog",
            fields=[
                ("sequence", models.BigAutoField(primary_key=True, serialize=False)),
                ("resource_type", models.CharField(max_length=80)),
                ("resource_uuid", models.CharField(max_length=80)),
                ("operation", models.CharField(max_length=20)),
                ("payload", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("device", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="mobile_api.mobiledevice")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={"indexes": [models.Index(fields=["user", "sequence"], name="mobile_change_cursor_idx")]},
        ),
        migrations.CreateModel(
            name="ApiIdempotencyRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.UUIDField()),
                ("endpoint", models.CharField(max_length=120)),
                ("request_hash", models.CharField(max_length=64)),
                ("response_status", models.PositiveSmallIntegerField()),
                ("response_body", models.JSONField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField()),
                ("device", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="mobile_api.mobiledevice")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "indexes": [models.Index(fields=["expires_at"], name="mobile_idem_expiry_idx")],
                "constraints": [models.UniqueConstraint(fields=("user", "device", "key"), name="unique_mobile_idempotency_key")],
            },
        ),
    ]
