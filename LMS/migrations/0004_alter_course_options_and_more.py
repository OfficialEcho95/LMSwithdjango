# Generated by Django 5.1.3 on 2024-11-20 07:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LMS', '0003_user_role_delete_userprofile'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ['-created_at']},
        ),
        migrations.RenameField(
            model_name='enrollment',
            old_name='enrolled_at',
            new_name='enrollment_date',
        ),
        migrations.AddField(
            model_name='course',
            name='difficulty_level',
            field=models.CharField(choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')], default='beginner', max_length=15),
        ),
        migrations.AddField(
            model_name='course',
            name='is_deleted',
            field=models.BooleanField(default=False, help_text='Mark as true to archive the course'),
        ),
        migrations.AddField(
            model_name='course',
            name='is_free',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='course',
            name='is_published',
            field=models.BooleanField(default=False, help_text='Set to true when the course is ready for students'),
        ),
        migrations.AddField(
            model_name='course',
            name='objectives',
            field=models.TextField(blank=True, help_text='Key objectives of the course', null=True),
        ),
        migrations.AddField(
            model_name='course',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='course',
            name='slug',
            field=models.SlugField(blank=True, help_text='URL-friendly identifier for the course', unique=True),
        ),
        migrations.AddField(
            model_name='course',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='course_thumbnails/'),
        ),
        migrations.AddField(
            model_name='course',
            name='video_intro',
            field=models.FileField(blank=True, null=True, upload_to='course_videos/'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='completion_date',
            field=models.DateTimeField(blank=True, help_text='Date of course completion', null=True),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='feedback',
            field=models.TextField(blank=True, help_text='Optional feedback from the student', null=True),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='progress',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Completion percentage', max_digits=5),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('completed', 'Completed'), ('dropped', 'Dropped')], default='active', max_length=10),
        ),
        migrations.AlterField(
            model_name='course',
            name='title',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='enrollment',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='LMS.course'),
        ),
        migrations.AlterField(
            model_name='enrollment',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='enrollment',
            constraint=models.UniqueConstraint(fields=('student', 'course'), name='unique_enrollment'),
        ),
    ]
