from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [("documents", "0001_initial")]
    operations = [
        migrations.AddField(model_name="evidencedocument", name="captured_at", field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name="evidencedocument", name="latitude", field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, validators=[django.core.validators.MinValueValidator(-90), django.core.validators.MaxValueValidator(90)])),
        migrations.AddField(model_name="evidencedocument", name="longitude", field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)])),
        migrations.AddField(model_name="evidencedocument", name="location_accuracy_metres", field=models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True, validators=[django.core.validators.MinValueValidator(0)])),
    ]
