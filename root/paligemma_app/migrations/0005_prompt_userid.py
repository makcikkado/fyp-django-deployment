# Generated by Django 4.2 on 2025-05-26 15:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('paligemma_app', '0004_alter_prompt_imageprompt'),
    ]

    operations = [
        migrations.AddField(
            model_name='prompt',
            name='userID',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
