"""
this houses the code to initialize and verify the payments and also call the 
paystack.py file
"""

from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from .paystack import Paystack
from LMS.models import Course, User


def initialize_payment(request, course_id, email, amount):
    """
    Initializes a payment transaction with Paystack, including course metadata.
    """
    amount = float(amount)
    if not email or not amount:
        return JsonResponse({"error": "Email and amount are required."}, status=400)

    course = get_object_or_404(Course, id=course_id)

    # Add metadata to the transaction
    metadata = {"course_id": course_id}

    # Initialize the Paystack transaction
    paystack = Paystack()
    response = paystack.initialize_transaction(email, amount, metadata)

    if response["status"]:
        return redirect(response["data"]["authorization_url"]) 
    else:
        return JsonResponse({"error": "Payment initialization failed"}, status=400)


def verify_payment(request, reference):
    """
    Verifies the payment transaction with Paystack and adds the course to the student's profile.
    """
    paystack = Paystack()
    response = paystack.verify_transaction(reference)

    if response["status"] and response["data"]["status"] == "success":
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"error": "User authentication required."}, status=403)

        # Extract course ID from metadata
        course_id = response["data"]["metadata"]["course_id"]
        if not course_id:
            return JsonResponse({"error": "Course metadata is missing."}, status=400)

        course = get_object_or_404(Course, id=course_id)

        # Add the course to the student's profile
        user.courses_purchased.add(course)
        course.enrolled_students.add(user)

        return redirect("student_courses", user_id=user.id)
    else:
        return JsonResponse({"error": "Payment verification failed"}, status=400)
