# Generated by Django 5.1.3 on 2024-12-06 07:10

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LMS', '0017_alter_course_is_free'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='instructor',
            field=models.ManyToManyField(limit_choices_to={'role': 'instructor'}, related_name='lessons_as_instructor', to=settings.AUTH_USER_MODEL),
        ),
    ]
