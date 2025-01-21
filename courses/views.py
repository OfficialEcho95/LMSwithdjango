from django.shortcuts import render, get_object_or_404, redirect
from LMS.models import Course, User, Enrollment, UserProgress
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseServerError
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.db import DatabaseError
import logging
import json

logger = logging.getLogger(__name__)


@login_required
def course_list(request):
    try:
        courses = Course.objects.prefetch_related("lessons", "instructor").all()
        for course in courses:
            course.can_delete = request.user.is_authenticated and (
                request.user.is_superuser
                or course.instructor.filter(id=request.user.id).exists()
            )
        return render(request, "courses/course_list.html", {"courses": courses})
    except DatabaseError as e:
        messages.error(request, "An error occurred while fetching the courses.")
        return HttpResponseServerError("Error fetching courses.", e)


@login_required
def course_detail(request, course_id):
    # Get the course object
    course = get_object_or_404(Course, id=course_id)

    price = course.price
    if price == None:
        price = 0
    user_email = request.user.email

    # Check if the user is an instructor for this course
    user_is_instructor = request.user in course.instructor.all()

    # Get all lessons for the course and select the first one if available
    lessons = course.lessons.all()
    lesson = lessons.first() if lessons.exists() else None
    student_confirmation = ""
    # print(request.user.email)
    for student in course.enrolled():
        student_confirmation = request.user.email == student.email

    # Pass data to the context
    context = {
        "course": course,
        "user_is_instructor": user_is_instructor,
        "lesson": lesson,
        "user_email": user_email,
        "price": price,
        "student_confirmation": student_confirmation,
    }
    return render(request, "courses/course_detail.html", context)


@login_required
def quiz_list(request, course_id):
    try:
        course = get_object_or_404(Course, id=course_id)
        quizzes = course.quizzes.all()
        return render(
            request, "courses/quiz_list.html", {"course": course, "quizzes": quizzes}
        )
    except Course.DoesNotExist:
        messages.error(request, "The requested course does not exist.")
        return redirect("course_list")
    except Exception as e:
        messages.error(request, "An error occurred while fetching the quizzes.")
        return HttpResponseServerError("Error fetching quizzes.")


@login_required
def add_course(request):
    try:
        logger.info(f"User {request.user.username} is attempting to add a course.")

        # Check if the user is an instructor
        if request.user.role != "instructor":
            logger.warning(
                f"User {request.user.username} is not an instructor and cannot add courses."
            )
            return HttpResponseForbidden("You are not authorized to add courses.")

        if request.method == "POST":
            logger.info("Processing POST request.")

            # Log the incoming data for debugging
            logger.debug(f"Request POST data: {request.POST}")
            logger.debug(f"Request FILES data: {request.FILES}")

            title = request.POST.get("title")
            description = request.POST.get("description")
            objectives = request.POST.get("objectives")
            instructor_ids = list(map(int, request.POST.getlist("instructors[]")))
            is_free = "is_free" in request.POST
            price = request.POST.get("price") if not is_free else None
            is_published = "is_published" in request.POST
            thumbnail = request.FILES.get("thumbnail")
            video_intro = request.FILES.get("video_intro")

            # Validate input
            if not title or not description:
                logger.warning("Title or description is missing.")
                messages.error(request, "Both title and description are required.")
                return render(request, "courses/add_course.html")

            if not instructor_ids:
                logger.warning("No instructors selected.")
                messages.error(request, "At least one instructor must be selected.")
                return render(request, "courses/add_course.html")

            if price and not price.isdigit():
                logger.warning(f"Invalid price value: {price}")
                messages.error(request, "Price must be a valid number.")
                return render(request, "courses/add_course.html")

            if video_intro and not video_intro.name.endswith((".mp4", ".mov", ".avi")):
                logger.warning("Invalid video file type.")
                messages.error(
                    request, "Video intro must be a valid video file (mp4, mov, avi)."
                )
                return render(
                    request,
                    "courses/add_course.html",
                )

            # Create the course
            logger.info(f"Creating course with title: {title}")
            course = Course.objects.create(
                title=title,
                description=description,
                objectives=objectives,
                is_free=is_free,
                price=price,
                is_published=is_published,
                thumbnail=thumbnail,
                video_intro=video_intro,
            )

            # Assign instructors to the course
            instructors = User.objects.filter(id__in=instructor_ids, role="instructor")
            if not instructors.exists():
                logger.warning("Invalid instructors provided.")
                messages.error(request, "Invalid instructors provided.")
                return render(
                    request,
                    "courses/add_course.html",
                )

            course.instructor.set(instructors)
            course.save()

            logger.info(f"Course '{title}' added successfully.")
            messages.success(request, "Course added successfully!")
            return redirect("course_list")

        # Make sure to pass instructors to the template
        instructors = User.objects.filter(role="instructor")
        return render(
            request,
            "courses/add_course.html",
            {"instructors": instructors},
        )

    except DatabaseError as e:
        logger.error(f"Database error occurred: {e}")
        messages.error(request, "An error occurred while adding the course.")
        return HttpResponseServerError("Error adding course.")
    except Exception as e:
        logger.exception(f"Unexpected error occurred: {e}")
        messages.error(request, "An unexpected error occurred.")
        return HttpResponseServerError("Unexpected error.")


@login_required
def delete_course(request, course_id):
    try:
        course = get_object_or_404(Course, id=course_id)
        course_instructor = course.course_instructor()

        # Check if the user is an instructor of the course or an admin
        if request.user.is_superuser or (request.user.id in [course_instructor]):
            # Delete the course
            course_title = course.title
            course.delete()
            messages.success(
                request, f'Course "{course_title}" has been successfully deleted.'
            )
            return redirect("course_list")
        else:
            messages.error(request, "You do not have permission to delete this course.")
            return HttpResponseForbidden(
                "You do not have permission to delete this course."
            )
    except Course.DoesNotExist:
        messages.error(request, "The course you are trying to delete does not exist.")
        return redirect("course_list")
    except Exception as e:
        messages.error(request, "An unexpected error occurred. Please try again later.")
        return HttpResponseServerError("An unexpected error occurred.")


@login_required
def enroll_in_course(request, course_id, email, amount):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method."})

    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "error": "You must be logged in as a student to enroll."}
        )

    # Update the user's email if provided
    request.user.email = email
    user = request.user.save()

    try:
        # Fetch the course
        course = get_object_or_404(Course, id=course_id)
        course.price = amount

        # Check if the student is already enrolled
        if Enrollment.objects.filter(student=request.user, course=course).first():
            return JsonResponse(
                {"success": False, "error": "You are already enrolled in this course."}
            )

        # Check if the course is free or paid
        if course.price == 0:
            user.courses_purchased.add(course)
            course.enrolled_students.add(user)
            enrollement_object = Enrollment.objects.create(
                student=request.user, course=course
            )
            return redirect("student_courses", user_id=user.id)

        return redirect(
            "initialize_payment", course_id=course.id, amount=amount, email=email
        )

    except Course.DoesNotExist:
        return JsonResponse({"success": False, "error": "The course does not exist."})

    except ValidationError as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def update_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    instructors = User.objects.filter(role="instructor")
    selected_instructor_ids = list(course.instructor.values_list("id", flat=True))
    course_instructor = course.course_instructor()

    # Permission check
    if not (request.user.is_superuser or request.user.id in [course_instructor]):
        return HttpResponseForbidden("You are not allowed to make this request.")

    if request.method == "POST":
        try:
            # Fetch form data
            title = request.POST.get("title", course.title)
            description = request.POST.get("description", course.description)
            objectives = request.POST.get("objectives", course.objectives)
            price = request.POST.get("price", 0)
            is_free = request.POST.get("is_free", str(course.is_free)).lower() == "true"
            instructor_ids = request.POST.getlist("instructors")

            # File uploads
            thumbnail = request.FILES.get("thumbnail")
            video_intro = request.FILES.get("video_intro")

            # Validation
            if not title:
                messages.error(request, "Course title cannot be empty.")
                raise ValueError("Invalid title")

            if not description:
                messages.error(request, "Course description cannot be empty.")
                raise ValueError("Invalid description")

            if not is_free:
                try:
                    price = float(price)
                    if price <= 0:
                        raise ValueError
                except ValueError:
                    messages.error(
                        request, "Price must be a positive number for paid courses."
                    )
                    raise ValueError("Invalid price")

            if instructor_ids:
                valid_instructors = User.objects.filter(
                    id__in=instructor_ids, role="instructor"
                )
                if not valid_instructors.exists():
                    messages.error(
                        request, "At least one valid instructor must be selected."
                    )
                    raise ValueError("Invalid instructors")
                course.instructor.set(valid_instructors)

            # Update course fields
            course.title = title
            course.description = description
            course.objectives = objectives
            course.price = price if not is_free else 0
            course.is_free = is_free

            # Update files if provided
            if thumbnail:
                course.thumbnail = thumbnail
            if video_intro:
                course.video_intro = video_intro

            course.save()

            messages.success(request, "Course updated successfully!")
            return redirect("course_detail", course_id=course.id)

        except ValueError as e:
            logger.error(f"Course update failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            messages.error(request, "An unexpected error occurred.")

    # Render the update form with existing data
    return render(
        request,
        "courses/update_course.html",
        {
            "course": course,
            "instructors": instructors,
            "selected_instructor_ids": selected_instructor_ids,
        },
    )


@login_required
def course_offered_by_student(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.user != user and not request.user.is_staff:
        return HttpResponseForbidden(
            "You do not have permission to view these courses."
        )

    student_course = user.courses_purchased.all()
    context = {"courses": student_course, "user_id": request.user.id}
    return render(request, "courses/student_courses.html", context)


@login_required
def remove_course_by_user(request, user_id, course_id):
    user = get_object_or_404(User, id=user_id)

    if request.user != user and not request.user.is_staff:
        return HttpResponseForbidden(
            "You do not have permission to perform this action."
        )

    course_to_remove = user.courses_purchased.filter(id=course_id).first()
    if not course_to_remove:
        return HttpResponseForbidden("Course not found in user's purchased list.")

    user.courses_purchased.remove(course_to_remove)

    return redirect("student_courses", user_id=user.id)


@csrf_exempt
def update_progress(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            course_id = data.get("course_id")
            progress = data.get("progress")

            user = request.user
            course = Course.objects.get(id=course_id)

            user_progress, created = UserProgress.objects.get_or_create(
                user=user, course=course
            )
            user_progress.progress = progress
            user_progress.save()

            return JsonResponse(
                {"success": True, "message": "Progress updated successfully!"}
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method."})


@login_required
def learning(request, course_title, user_email):
    course = get_object_or_404(Course, title=course_title)
    lessons = course.lessons.prefetch_related("video_url", "media_file").all()
    grade = request.GET.get("grade")
    progress = request.GET.get("progress")

    for lesson in lessons:
        local_videos = lesson.media_file.all()
        link_videos = lesson.video_url.all()

        # for debug purpose these 2
        for video in link_videos:
            video.url
        for video in local_videos:
            video.file

    instructors = course.instructor.all()
    for instructor in instructors:
        instructor.username
    context = {
        "user_email": request.user.email,
        "course": course,
        "lessons": lessons,
        "lesson_id": lesson.id,
        "instructors": instructor,
        "progress": progress,
        "grade": grade
    }
    print(lesson.id)

    return render(request, "courses/learning.html", context)
