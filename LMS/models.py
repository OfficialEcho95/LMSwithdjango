from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.http import HttpResponseForbidden


class User(AbstractUser):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("instructor", "Instructor"),
        ("admin", "Admin"),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")

    # Field to store the student's grade
    grade = models.FloatField(
        null=True, blank=True, help_text="Grade for the student", default=0
    )

    # Override groups and permissions fields for clarity
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )
    courses_purchased = models.ManyToManyField(
        "Course",
        related_name="purchased_courses",
        blank=True,
    )
    socket_id = models.CharField(max_length=255, null=True, blank=True, unique=True)

    def __str__(self):
        return self.email

    def get_student_grade(self, course_id):
        """
        Returns the grade if the user is a student, otherwise None.
        """
        if self.role == "student":
            return self.courses_purchased

        return None

    def purchased_courses(self):
        if self.role != "student":
            return HttpResponseForbidden
        return self.courses_purchased.all()


class Course(models.Model):
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(help_text="Brief description of the course")
    objectives = models.TextField(
        blank=True, null=True, help_text="Key objectives of the course"
    )
    level_choices = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]
    instructor = models.ManyToManyField(
        User,
        related_name="courses_as_instructor",
        limit_choices_to={"role": "instructor"},
    )
    students = models.ManyToManyField(
        User, through="Enrollment", related_name="courses_as_student"
    )
    thumbnail = models.ImageField(upload_to="course_thumbnails/", blank=True, null=True)
    video_intro = models.FileField(upload_to="course_videos/", blank=True, null=True)
    is_free = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    is_published = models.BooleanField(
        default=True, help_text="Set to true when the course is ready for students"
    )
    enrolled_students = models.ManyToManyField(
        "User", related_name="enrolled_students", blank=True
    )
    is_deleted = models.BooleanField(
        default=False, help_text="Mark as true to archive the course"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("course_detail", kwargs={"course_id": self.id})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.is_free and self.price not in (None, 0):
            raise ValidationError(
                "Free courses must have a price of 0 or be left blank."
            )
        if not self.is_free and (self.price is None or self.price <= 0):
            raise ValidationError("Paid courses must have a valid positive price.")

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def enrolled(self):
        return self.enrolled_students.all()

    def course_instructor(self):
        if self.instructor.count() > 1:
            return list(self.instructor.values_list("id", flat=True))
        instructor = self.instructor.values("id").first()
        return instructor["id"] if instructor else None

    class Meta:
        ordering = ["-created_at"]


class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )  # Progress in percentage
    last_accessed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.course.title}: {self.progress}%"


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    instructor = models.ManyToManyField(
        User,
        related_name="lessons_as_instructor",
        limit_choices_to={"role": "instructor"},
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    video_url = models.ManyToManyField("Video", blank=True)
    media_file = models.ManyToManyField("MediaFile", blank=True)
    order = models.PositiveIntegerField(default=1)
    duration = models.PositiveIntegerField(
        help_text="Duration in minutes", null=True, blank=True
    )
    is_passed = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    prerequisite_lessons = models.ManyToManyField(
        "self", blank=True, related_name="next_lessons"
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["order"]


class Video(models.Model):
    url = models.URLField()


class MediaFile(models.Model):
    file = models.FileField(upload_to="lesson_media/")


class Enrollment(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrollments"
    )
    enrollment_date = models.DateTimeField(auto_now_add=True)
    progress = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, help_text="Completion percentage"
    )
    completion_date = models.DateTimeField(
        blank=True, null=True, help_text="Date of course completion"
    )
    feedback = models.TextField(
        blank=True, null=True, help_text="Optional feedback from the student"
    )
    status_choices = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("dropped", "Dropped"),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default="active")

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"], name="unique_enrollment"
            )
        ]


class Question(models.Model):
    question_text = models.TextField()
    is_true = models.BooleanField(default=False)
    assignment = models.ForeignKey(
        "Assignment", on_delete=models.CASCADE, related_name="questions", default=1
    )

    def clean(self):
        # Ensure MCQ questions have at least one correct choice
        if (
            self.question_type == "true/false"
            and not self.choices.filter(is_correct=True).exists()
        ):
            raise ValidationError(
                "True/False questions must have at least one correct choice."
            )

    def __str__(self):
        return self.question_text

# Assignment Model
class Assignment(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="assignments"
    )
    question = models.ManyToManyField(
        "Question", related_name="assignments", blank=True
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="lesson_assignments",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    is_published = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    max_grade = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    file = models.FileField(upload_to="assignments/", blank=True, null=True)
    is_graded = models.BooleanField(default=False)
    students_submitted = models.ManyToManyField(
        User, related_name="submitted_assignments", blank=True
    )
    feedback = models.TextField(blank=True, null=True)
    prerequisite_assignments = models.ManyToManyField(
        "self", blank=True, related_name="next_assignments"
    )

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        self.student.courses_purchased.remove(self.course)
        self.student.enrolled_courses.remove(self.course)

        # Now delete the enrollment object itself
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ["due_date"]


# Assignment Submission Model
class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="submissions"
    )
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="submissions",
        null=True, blank=True
    )
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="submissions"
    )

    is_correct = models.BooleanField(default=False)
    submission_file = models.FileField(
        upload_to="assignments/"
    )  # assignments/ dir is in media dir
    student_answers = models.JSONField(default=dict)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission by {self.student.username} who scored {self.grade} for {self.assignment.title}"

    def is_graded(self):
        return self.grade is not None

    class Meta:
        ordering = ["submitted_at"]


class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="quizzes")
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    time_limit = models.DurationField(
        null=True, blank=True, help_text="Time limit for the quiz"
    )
    passing_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Score required to pass",
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="quiz_attempts"
    )
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status_choices = [
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("timed_out", "Timed Out"),
    ]
    status = models.CharField(
        max_length=20, choices=status_choices, default="in_progress"
    )
    time_taken = models.DurationField(null=True, blank=True)

    def complete_attempt(self, score, time_taken):
        self.score = score
        self.time_taken = time_taken
        self.status = "completed"
        self.completed_at = timezone.now()
        self.save()

    def __str__(self):
        return f"Attempt by {self.student.username} for {self.quiz.title}"

    class Meta:
        ordering = ["-completed_at"]


class Message(models.Model):
    sender = models.ForeignKey(
        User, related_name="sent_messages", on_delete=models.CASCADE
    )
    recipient = models.ForeignKey(
        User, related_name="received_messages", on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username} at {self.timestamp}"
