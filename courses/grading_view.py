from django.core.exceptions import ObjectDoesNotExist
from .models import User
from django.shortcuts import render
from django.contrib import messages
import openpyxl
from django.http import HttpResponse


def process_grades_from_file(file):
    """
    Reads an uploaded Excel file, extracts student details (username, ID, grade),
    and assigns grades cumulatively.
    """
    try:
        # Load the workbook and the first sheet
        workbook = openpyxl.load_workbook(file)
        sheet = workbook.active

        for row in sheet.iter_rows(min_row=2, values_only=True):  # Skip the header row
            username, user_id, grade = row

            try:
                # Ensure data validity
                if not username or not user_id or grade is None:
                    print(f"Skipping invalid row: {row}")
                    continue

                # Get the student user
                user = User.objects.get(username=username, id=user_id)

                # Assign grade
                assign_grade(user, float(grade))

                print(f"Assigned grade {grade} to {username} (ID: {user_id}).")

            except ObjectDoesNotExist:
                print(f"User {username} with ID {user_id} not found. Skipping row.")
            except ValueError as e:
                print(f"Error assigning grade for {username}: {e}")
            except Exception as e:
                print(f"Unexpected error for {username}: {e}")

        print("Grade processing complete.")
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")


def upload_grades(request):
    """
    View to upload grades from an Excel file.
    """
    if request.method == "POST":
        file = request.FILES.get("file")

        if file:
            try:
                process_grades_from_file(file)
                messages.success(request, "Grades uploaded and processed successfully!")
            except Exception as e:
                messages.error(request, f"Error processing grades: {e}")
        else:
            messages.error(request, "No file uploaded.")

    return render(request, "courses/upload_grades.html")


def assign_grade(user, new_grade):
    """
    Assigns a new grade to the student by adding it to their current grade.
    The grade is added cumulatively.
    """
    if new_grade < 0:
        raise ValueError("Grade cannot be negative.")

    try:
        current_grade = user.grade if user.grade else 0
        total_grade = current_grade + new_grade

        # Update the user's grade with the new cumulative grade
        user.grade = total_grade
        user.save()

        print(f"Updated {user.username}'s grade to {total_grade}.")
    except Exception as e:
        print(f"Error assigning grade to {user.username}: {e}")

# this would be completed and integrated into the system