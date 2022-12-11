from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core.models import User
from django.utils.translation import gettext_lazy as _


# Register your models here.
class UserAdmin(BaseUserAdmin):
    ordering = ["id"]
    list_display = [
        "email",
        "first_name",
        "last_name",
        "last_login_humanize",
        "date_joined_humanize",
    ]
    fieldsets = (
        (
            None,
            {"fields": ("email", "password")},
        ),
        (
            _("Permissions"),
            {"fields": ("is_active", "is_staff", "is_superuser")},
        ),
        (
            _("Important dates"),
            {"fields": ("last_login", "date_joined")},
        ),
    )
    readonly_fields = ["last_login", "date_joined"]
    # used when creating new user via admin panel
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_active"),
            },
        ),
    )


admin.site.register(User, UserAdmin)
