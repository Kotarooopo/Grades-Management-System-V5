# Generated by Django 5.0.4 on 2024-11-08 01:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_class_scores_visible'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='class',
            name='scores_visible',
        ),
    ]
