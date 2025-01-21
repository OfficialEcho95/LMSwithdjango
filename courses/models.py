from django.core.exceptions import ValidationError
from LMS.models import Course, Enrollment
from django.shortcuts import redirect


def enroll_student_in_course(student, course_id):
    """
    Enrolls a student in a course if they are not already enrolled.

    :param student: The user object (student) attempting to enroll.
    :param course_id: The ID of the course the student wants to enroll in.
    :raises ValidationError: If the student is already enrolled or if the course is not available.
    """
    try:
        # Fetch the course
        course = Course.objects.get(id=course_id)

        # Check if the student is already enrolled
        if Enrollment.objects.filter(student=student, course=course).exists():
            raise ValidationError("You are already enrolled in this course.")

        # # Check if the course is published
        # if not course.is_published:
        #     raise ValidationError("This course is not available for enrollment.")

        if course.price == 0 or course.is_free:
            # Enroll the student
            Enrollment.objects.create(student=student, course=course)
            return f"Successfully enrolled in the course: {course.title}"

        return redirect("initialize_payment")

    except Course.DoesNotExist:
        raise ValidationError("The course does not exist.")
