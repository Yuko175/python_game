# Generated by Django 5.1 on 2024-08-28 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rose', '0002_remove_cell_value_cell_content_alter_cell_col_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cell',
            name='content',
            field=models.CharField(default='', max_length=1),
        ),
    ]
