# Generated by Django 5.1.3 on 2024-11-17 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0015_certificate_signature_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='website',
            field=models.URLField(blank=True, null=True),
        ),
    ]
