# Generated by Django 5.1.5 on 2025-02-04 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_comment_entity_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='avatar_url',
        ),
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/'),
        ),
    ]
