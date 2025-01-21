from django.contrib import admin
from LMS.models import User, Course


class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_staff", "is_active")  # Fields to display
    search_fields = ("username", "email")  # Fields to search
    list_filter = ("is_staff", "is_active")  # Filters in the sidebar


admin.site.register(User, UserAdmin)
