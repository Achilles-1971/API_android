# Generated by Django 5.1.6 on 2025-02-19 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_event_image_place_added_by_place_is_approved_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email_verification_code',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='is_email_confirmed',
            field=models.BooleanField(default=False),
        ),
    ]
