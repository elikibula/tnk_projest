from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("audit", "0001_initial"),
        ("locations", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="auditevent",
            name="province",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="audit_events",
                to="locations.province",
            ),
        ),
        migrations.AddField(
            model_name="auditevent",
            name="tikina",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="audit_events",
                to="locations.tikina",
            ),
        ),
        migrations.AddField(
            model_name="auditevent",
            name="village",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="audit_events",
                to="locations.village",
            ),
        ),
    ]
