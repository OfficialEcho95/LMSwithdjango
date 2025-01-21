# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import User


# @admin.register(User)
# class CustomUserAdmin(UserAdmin):
#     fieldsets = (
#         (None, {"fields": ("username", "password")}),
#         ("Personal info", {"fields": ("first_name", "last_name", "email")}),
#         ("Permissions", {"fields": ("role", "groups", "user_permissions")}),
#         ("Important dates", {"fields": ("last_login", "date_joined")}),
#     )
#     add_fieldsets = (
#         (
#             None,
#             {
#                 "classes": ("wide",),
#                 "fields": ("username", "password1", "password2", "role"),
#             },
#         ),
#     )
#     list_display = ("username", "email", "role", "is_active", "is_staff")
#     list_filter = ("role", "is_staff", "is_superuser", "is_active")
