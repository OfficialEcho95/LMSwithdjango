from django.shortcuts import render, get_object_or_404, redirect
from LMS.models import Course, Lesson, User, Video, MediaFile
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseServerError
from django.contrib import messages
from .form import LessonForm

@login_required
def lesson_list(request, course_id):
    try:
        course = get_object_or_404(Course, id=course_id)
        lessons = course.lessons.all().order_by("order")
        return render(
            request, "courses/lesson_list.html", {"course": course, "lessons": lessons}
        )
    except Course.DoesNotExist:
        messages.error(request, "The requested course does not exist.")
        return redirect("course_list")
    except Exception as e:
        messages.error(request, "An error occurred while fetching the lessons.")
        return HttpResponseServerError("Error fetching lessons.")


@login_required
def add_lesson_to_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    instructors = User.objects.filter(role="instructor")

    if request.user.role != "instructor":
        return HttpResponseForbidden("You do not have permission to add lessons.")

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        video_urls = request.POST.getlist("video_url")  # Allows multiple URLs
        media_files = request.FILES.getlist("media_file")  # Allows multiple files
        instructor_ids = request.POST.getlist("instructors")

        # Create the Lesson instance
        lesson = Lesson(
            course=course,
            title=title,
            content=content,
        )
        lesson.save()

        # Add videos
        for video_url in video_urls:
            video = Video.objects.create(url = video_url)
            lesson.video_url.add(video)

        # Add media files
        for media_file in media_files:
            media = MediaFile.objects.create(file=media_file)
            lesson.media_file.add(media)

        # Associate instructors with the lesson
        if instructor_ids:
            instructors_to_add = User.objects.filter(
                id__in=instructor_ids, role="instructor"
            )
            lesson.instructors.set(instructors_to_add)

        print("Successfully saved lesson to course.")
        return redirect("course_detail", course_id=course.id)

    print("An error occurred.")
    return render(
        request,
        "courses/add_lesson.html",
        {
            "course": course,
            "instructors": instructors,
        },
    )


# function to delete a lesson of a course
@login_required
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    # Check if the user is an instructor of the course or an admin
    if request.user.is_superuser or (
        request.user.role == "instructor"
        and lesson.course.instructor.filter(id=request.user.id).exists()
    ):
        # Delete the lesson
        lesson.delete()
        messages.success(
            request, f'Lesson "{lesson.title}" has been successfully deleted.'
        )
    else:
        messages.error(request, "You do not have permission to delete this lesson.")

    return redirect("course_detail", course_id=lesson.course.id)

@login_required
def update_lesson_view(request, lesson_id):
    if request.user.role != "instructor":
        return HttpResponseForbidden("You do not have permission to update lessons.")

    # Retrieve the lesson object
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.method == "POST":
        # Process the form with submitted data
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()
            return redirect("course_detail", course_id=lesson.course.id)
    else:
        # Pre-fill the form with the current lesson data
        form = LessonForm(instance=lesson)

    return render(
        request, "courses/update_lesson.html", {"form": form, "lesson": lesson}
    )

# function to get lessons of each course
@login_required
def get_lessons_view(request, course_id, lesson_id):
    try:
        course = get_object_or_404(Course, id=course_id)
        lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
        user_is_instructor = request.user.role == "instructor"

        return render(
            request,
            "courses/lesson_details.html",
            {"course": course, "lesson": lesson, "user_email": request.user.email, "user_is_instructor": user_is_instructor},
        )

    except Exception as e:
        # Log the error and send a response to the client
        messages.error(request, f"An error occurred: {str(e)}")
        return HttpResponseServerError("Error fetching lesson.")
 