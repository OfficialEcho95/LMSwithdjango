# Generated by Django 5.1.3 on 2024-12-28 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("LMS", "0033_assignmentsubmission_student_answers_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="assignmentsubmission",
            name="is_correct",
            field=models.BooleanField(default=False),
        ),
    ]
