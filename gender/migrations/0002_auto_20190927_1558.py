# Generated by Django 2.2.5 on 2019-09-27 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gender', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='noun',
            name='female_up',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='noun',
            name='male_up',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
