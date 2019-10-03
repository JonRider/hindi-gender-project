# Generated by Django 2.2.5 on 2019-10-03 15:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gender', '0007_auto_20191002_2024'),
    ]

    operations = [
        migrations.AddField(
            model_name='noun',
            name='submitted_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
