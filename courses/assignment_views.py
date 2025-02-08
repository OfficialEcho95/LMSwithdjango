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

        for assignment in assignments:
            questions = assignment.questions.all()
            for question in questions:
                # print (f"{question}: {question.is_true}")
                pass

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


def submit_assignment_view(request, course_id, lesson_id, assignment_id):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    assignment = get_object_or_404(Assignment, id=assignment_id, lesson=lesson, course=course)

    if request.method == "POST":
        student_answers = {}
        correct_answers = 0
        questions = assignment.questions.all()

        # Collect and grade the answers
        for question in questions:
            answer = request.POST.get(f"answer_{question.id}")  # Get the student's answer

            if answer is not None:
                # Check if the answer is correct and store the result
                is_correct = (answer.lower() == "true") == question.is_true #explicity converts string to bool
                print(is_correct)
                print(answer, question.is_true)
                student_answers[question.id] = is_correct  # Store True/False answers
                if is_correct:
                    correct_answers += 1
        print(correct_answers)

        # Create a submission record and save the answers
        submission = AssignmentSubmission.objects.create(
            assignment=assignment,
            student=request.user,
            grade=None,  # Placeholder; will update after grading
            feedback=None,
        )

        # Calculate the grade
        grade = (correct_answers / len(questions)) * 100 if questions else 0
        submission.grade = grade
        print(f"Grade for assignment {assignment.title}: {grade:.2f}")

        # Add feedback
        submission.feedback = "Great job!" if grade >= 70 else "Needs improvement."
        submission.save()

        if grade >= 70:
            lesson.is_passed = True
            lesson.save()

        # Log the successful submission
        print(
            f"Assignment {assignment.title} submitted successfully with grade {grade:.2f} for user {request.user}"
        )

        # Update user progress
        total_lessons = course.lessons.count()
        passed_lessons = course.lessons.filter(is_passed=True).count()
        progress_percentage = (
            (passed_lessons / total_lessons) * 100 if total_lessons else 0
        )
        print("progress %:", progress_percentage)

        user_progress, _ = UserProgress.objects.get_or_create(
            user=request.user, course=course
        )
        user_progress.progress = progress_percentage
        user_progress.save()

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
