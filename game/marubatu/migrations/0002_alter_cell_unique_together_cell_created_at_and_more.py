# Generated by Django 5.1 on 2024-08-22 13:59

import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marubatu', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cell',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='cell',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cell',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
