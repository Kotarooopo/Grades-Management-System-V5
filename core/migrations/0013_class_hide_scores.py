# Generated by Django 5.0.4 on 2024-11-08 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_remove_class_scores_visible'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='hide_scores',
            field=models.BooleanField(default=False),
        ),
    ]