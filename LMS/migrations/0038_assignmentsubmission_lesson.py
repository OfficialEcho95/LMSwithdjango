# Generated by Django 5.1.2 on 2025-02-07 13:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LMS', '0037_lesson_is_passed'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignmentsubmission',
            name='lesson',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='LMS.lesson'),
        ),
    ]
