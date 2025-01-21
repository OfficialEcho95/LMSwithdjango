from django.contrib import admin
from LMS.models import Course, Enrollment
from LMS.models import Quiz, Question, QuizAttempt, Lesson

class InstructorInline(admin.TabularInline):
    model = Course.instructor.through
    extra = 1 


class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "description_snippet", "created_at")
    search_fields = ("title", "description") 
    list_filter = ("created_at",)
    ordering = ("-created_at",)

    inlines = [InstructorInline]

    def description_snippet(self, obj):
        """Show a snippet of the course description."""
        return (
            obj.description[:50] + "..."
            if len(obj.description) > 50
            else obj.description
        )

    description_snippet.short_description = "Description"


class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "course",
        "enrollment_date",
        "status",
        "progress",
        "completion_date",
    ) 
    list_filter = ("status", "course") 
    search_fields = (
        "student__username",
        "course__title",
    )
    list_editable = (
        "status",
        "progress",
    )  # Make status and progress fields editable directly from the list view
    ordering = ["-enrollment_date"] 


class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "course",
        "order",
        "created_at",
    )
    list_filter = ("course", "order")
    search_fields = ("title", "course__title")


# Custom admin for Quiz
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "created_at")
    search_fields = ("title", "course__title")


# Custom admin for Question
# class QuestionAdmin(admin.ModelAdmin):
#     list_display = ("question_text", "quiz", "question_type")
#     list_filter = ("quiz", "question_type")
#     search_fields = ("question_text",)


# Custom admin for Choice
# class ChoiceAdmin(admin.ModelAdmin):
#     list_display = ("choice_text", "question", "is_correct")
#     list_filter = ("question", "is_correct")
#     search_fields = ("choice_text",)


# Custom admin for QuizAttempt
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("quiz", "student", "score", "completed_at")
    list_filter = ("quiz", "student")
    search_fields = ("student__username", "quiz__title")


# Register models with custom admins
admin.site.register(Quiz, QuizAdmin)
# admin.site.register(Question, QuestionAdmin)
# admin.site.register(Choice, ChoiceAdmin)
admin.site.register(QuizAttempt, QuizAttemptAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
