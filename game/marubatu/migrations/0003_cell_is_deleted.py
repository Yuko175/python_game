# Generated by Django 5.1 on 2024-08-22 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marubatu', '0002_alter_cell_unique_together_cell_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cell',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
