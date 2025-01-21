from django import forms
from LMS.models import Lesson, Assignment

'''
This will house all the forms for the project, for easy maintenance
'''
class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = [
            "title",
            "content",
            "video_url",
            "order",
            "duration",
            "is_published",
            "media_file",
        ]


class AssignmentForm(forms.ModelForm):
    pass
