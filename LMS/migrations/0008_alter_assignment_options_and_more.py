# Generated by Django 5.1.3 on 2024-11-22 03:35

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LMS', '0007_alter_course_is_free'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assignment',
            options={'ordering': ['due_date']},
        ),
        migrations.AlterModelOptions(
            name='assignmentsubmission',
            options={'ordering': ['submitted_at']},
        ),
        migrations.AlterModelOptions(
            name='lesson',
            options={'ordering': ['order']},
        ),
        migrations.AlterModelOptions(
            name='quiz',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='quizattempt',
            options={'ordering': ['-completed_at']},
        ),
        migrations.AddField(
            model_name='assignment',
            name='feedback',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='assignment',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='assignments/'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='assignment',
            name='is_graded',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='assignment',
            name='is_published',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='assignment',
            name='max_grade',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='assignment',
            name='prerequisite_assignments',
            field=models.ManyToManyField(blank=True, related_name='next_assignments', to='LMS.assignment'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='students_submitted',
            field=models.ManyToManyField(blank=True, related_name='submitted_assignments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assignment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='lesson',
            name='duration',
            field=models.PositiveIntegerField(blank=True, help_text='Duration in minutes', null=True),
        ),
        migrations.AddField(
            model_name='lesson',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='lesson',
            name='is_published',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='lesson',
            name='media_file',
            field=models.FileField(blank=True, null=True, upload_to='lesson_media/'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='prerequisite_lessons',
            field=models.ManyToManyField(blank=True, related_name='next_lessons', to='LMS.lesson'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='lesson',
            name='video_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='question',
            name='difficulty_level',
            field=models.CharField(choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], default='medium', max_length=20),
        ),
        migrations.AddField(
            model_name='quiz',
            name='passing_score',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Score required to pass', max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='quiz',
            name='time_limit',
            field=models.DurationField(blank=True, help_text='Time limit for the quiz', null=True),
        ),
        migrations.AddField(
            model_name='quizattempt',
            name='status',
            field=models.CharField(choices=[('in_progress', 'In Progress'), ('completed', 'Completed'), ('timed_out', 'Timed Out')], default='in_progress', max_length=20),
        ),
        migrations.AddField(
            model_name='quizattempt',
            name='time_taken',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='description',
            field=models.TextField(help_text='Brief description of the course'),
        ),
        migrations.AlterField(
            model_name='quizattempt',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
