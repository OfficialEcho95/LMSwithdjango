from LMS.models import (
    Course,
    Lesson,
    Assignment,
    Question,
    AssignmentSubmission,
    UserProgress,
)
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseServerError
from django.urls import reverse
import logging


def add_assignment_to_lesson(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    if request.method == "POST":
        # Retrieve form data
        assignment_title = request.POST.get("title")
        assignment_description = request.POST.get("description")
        due_date = request.POST.get("due_date")
        questions = request.POST.getlist("questions[]")
        answers = request.POST.getlist("answers[]")

        # Validate required fields
        if not assignment_title or not assignment_description:
            messages.error(request, "Title and description are required.")
            return redirect("add_assignment", course_id=course.id, lesson_id=lesson.id)

        if not questions or len(questions) != len(answers):
            messages.error(request, "Each question must have a corresponding answer.")
            return redirect("add_assignment", course_id=course.id, lesson_id=lesson.id)

        # Create the assignment
        assignment = Assignment.objects.create(
            title=assignment_title,
            description=assignment_description,
            course=course,
            lesson=lesson,
            due_date=due_date,
        )

        # Add questions to the assignment
        for question_text, answer in zip(questions, answers):
            Question.objects.create(
                question_text=question_text,
                is_true=(answer.lower() == "true"),
                assignment=assignment,
            )

        messages.success(
            request,
            f"Assignment '{assignment.title}' with {len(questions)} questions added.",
        )
        return redirect("course_detail", course_id=course.id)

    return render(
        request,
        "courses/add_assignment.html",
        {"course": course, "lesson": lesson},
    )


# function to get assignments of each lesson
def get_assignments_view(request, course_id, lesson_id):
    try:
        course = get_object_or_404(Course, id=course_id)
        lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
        assignments = lesson.lesson_assignments.all()

        print(request.GET.getlist(f"questions[]"))

        for assignment in assignments:
            questions = assignment.questions.all()
            # print(questions)

        is_instructor = (
            request.user.is_authenticated and request.user.role == "instructor"
        )

        return render(
            request,
            "courses/get_assignment.html",
            {
                "course": course,
                "lesson": lesson,
                "assignments": assignments,
                "is_instructor": is_instructor,
            },
        )
    except Exception as e:
        print(e)
        messages.error(request, "An error occurred while fetching the assignments.")
        return HttpResponseServerError("Error fetching assignments.", e)


# Get an instance of a logger
logger = logging.getLogger(__name__)

#still alot of wortk to be done here
def submit_assignment_view(request, course_id, lesson_id, assignment_id):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    assignment = get_object_or_404(
        Assignment, id=assignment_id, lesson=lesson, course=course
    )

    # Log the start of the submission
    logger.info(
        f"User {request.user} is submitting assignment {assignment.title} for course {course.title}"
    )

    if request.method == "POST":
        student_answers = {}
        correct_answers = 0
        questions = assignment.questions.all()

        print(request.POST.getlist(f"correct_answers[]")) # returns []
        print(request.POST.getlist(f"questions[]"))  # returns []
        print(request.POST.getlist(f"answers[]"))  # returns []

        # Collect and grade the answers
        for question in questions:
            answer = request.POST.get(
                f"answers_{question.id}"
            )  # Get the student's answer
            logger.debug(f"Answer for question {question.id}: {answer}")

            if answer is not None:
                # Check if the answer is correct and store the result
                is_correct = (answer.lower() == "true") == question.is_true
                student_answers[question.id] = is_correct  # Store True/False answers
                if is_correct:
                    correct_answers += 1

        # Ensure all questions are answered
        if len(student_answers) != questions.count():
            messages.error(
                request, "Please answer all the questions before submitting."
            )
            logger.warning(
                f"User {request.user} did not answer all questions for assignment {assignment.title}. Answered: {len(student_answers)}, Total Questions: {questions.count()}"
            )

            return render(
                request,
                "courses/submit_assignment.html",
                {
                    "course": course,
                    "lesson": lesson,
                    "assignment": assignment,
                },
            )

        # Create a submission record and save the answers
        submission = AssignmentSubmission.objects.create(
            assignment=assignment,
            student=request.user,
            grade=None,  # Placeholder; will update after grading
            feedback=None,
        )
        logger.info(
            f"Assignment submission created for user {request.user} and assignment {assignment.title}"
        )

        # Set the 'is_correct' field for each answer, ensuring no NULL values are saved
        for question in questions:
            is_correct = student_answers.get(
                question.id, False
            )  # Default to False if no answer
            submission.is_correct = is_correct  # Ensure it’s not NULL
            logger.debug(f"Set 'is_correct' for question {question.id}: {is_correct}")

        # Calculate the grade
        grade = (correct_answers / len(questions)) * 100 if questions else 0
        submission.grade = grade
        logger.info(f"Grade for assignment {assignment.title}: {grade:.2f}")

        # Add feedback
        submission.feedback = "Great job!" if grade >= 70 else "Needs improvement."
        submission.save()

        # Log the successful submission
        logger.info(
            f"Assignment {assignment.title} submitted successfully with grade {grade:.2f} for user {request.user}"
        )

        # Update user progress
        total_lessons = course.lessons.count()
        user_progress, _ = UserProgress.objects.get_or_create(
            user=request.user, course=course
        )

        # user_progress.progress = (
        #     len(user_progress) / total_lessons
        # ) * 100
        # user_progress.save()
        logger.info(f"User {request.user} updated progress for course {course.title}")

        messages.success(
            request, f"Assignment submitted successfully! Grade: {grade:.2f}"
        )

        # Redirect to the course page or a confirmation page to avoid resubmission
        return redirect("learning", course_title=course.title, user_email=request.user)

    # If the form is not submitted, just render the assignment page
    return render(
        request,
        "courses/submit_assignment.html",
        {
            "course": course,
            "lesson": lesson,
            "assignment": assignment,
        },
    )


# def submit_assignment_view(request, course_id, lesson_id, assignment_id):
#     try:
#         course = get_object_or_404(Course, id=course_id)
#         lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
#         assignment = get_object_or_404(Assignment, id=assignment_id, lesson=lesson)

#         if request.method == "POST":
#             print("Request POST data:", request.POST)
#             student_answers = request.POST.getlist("answers[]")
#             correct_answers = request.POST.getlist("correct_answers[]")
#             print("Student answers:", student_answers)
#             print("Correct answers:", correct_answers)

#             if len(student_answers) != len(correct_answers):
#                 messages.error(
#                     request, "Please answer all questions before submitting."
#                 )
#                 return redirect(
#                     "submit_assignment", course_id, lesson_id, assignment_id
#                 )

#             correct_count = sum(
#                 1
#                 for student, correct in zip(student_answers, correct_answers)
#                 if student == correct
#             )
#             grade = (correct_count / len(correct_answers)) * 100

#             AssignmentSubmission.objects.create(
#                 assignment=assignment,
#                 student=request.user,
#                 grade=grade,
#                 is_graded=True,
#                 feedback="Great job!" if grade >= 70 else "Needs improvement.",
#             )
#             assignment.students_submitted.add(request.user)

#             total_lessons = course.lessons.count()
#             user_progress, _ = UserProgress.objects.get_or_create(
#                 user=request.user, course=course
#             )

#             if lesson_id not in user_progress.completed_lessons:
#                 user_progress.completed_lessons.append(lesson_id)
#                 user_progress.progress = (
#                     len(user_progress.completed_lessons) / total_lessons
#                 ) * 100
#                 user_progress.save()

#             messages.success(
#                 request, f"Assignment submitted successfully! Your grade: {grade:.2f}%"
#             )
#             return redirect("learning", course_id=course.id)

#         return render(
#             request,
#             "courses/submit_assignment.html",
#             {"course": course, "lesson": lesson, "assignment": assignment},
#         )

#     except ZeroDivisionError as e:
#         print(f"ZeroDivisionError in submit_assignment_view: {e}")
#         messages.error(request, "No valid questions to grade.")
#         return redirect("submit_assignment", course_id, lesson_id, assignment_id)

#     except Exception as e:
#         print(f"Unexpected error in submit_assignment_view: {e}")
#         messages.error(request, "An unexpected error occurred.")
#         # return redirect("error_page")
