# Generated by Django 5.1.6 on 2025-03-21 19:52

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_comment_content_alter_comment_deleted_by_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='news',
            name='likes',
        ),
        migrations.AddField(
            model_name='news',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='liked_news', to=settings.AUTH_USER_MODEL),
        ),
    ]
