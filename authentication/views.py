from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from LMS.models import Course

def login_view(request):
    context = {}
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("home"))
        else:
            print("Authentication failed.")  # Debug failure
            context["error_message"] = "Invalid username or password."
    return render(request, "authentication/login.html", context)


def logout_view(request):
    logout(request)
    return redirect("login")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        confirm_password = request.POST.get("confirm_password")

        # Validate inputs
        if not username or not email or not password or not confirm_password:
            messages.error(request, "All fields are required!")
            return redirect("register")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("register")

        try:
            User = get_user_model()
            user = User.objects.create_user(
                username=username, password=password, email=email,
                first_name=first_name, last_name=last_name
            )
            user.save()
            login(request, user)  # Automatically log the user in
            messages.success(request, "Registration successful!")
            return redirect("home")
        except Exception as e:
            messages.error(request, f"Error during registration: {str(e)}")
            return redirect("register")

    return render(request, "authentication/register.html")


def home_view(request):
    courses = Course.objects.prefetch_related("lessons", "instructor").all()
    return render(request, "authentication/index.html", {"username": request.user.username, "courses": courses})
