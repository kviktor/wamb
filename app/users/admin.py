from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from app.users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "can_view",
                    "can_change",
                    "can_manage_users",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
