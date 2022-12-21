from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin import ModelAdmin
from core.models import User, CodeSpace
from django.utils.translation import gettext_lazy as _


# Register your models here.
class UserAdmin(BaseUserAdmin):
    ordering = ["date_joined"]
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
            {"fields": ("first_name", "last_name", "email")},
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


class CodeSpaceAdmin(ModelAdmin):
    ordering = ["created_at"]
    list_display = [
        "uuid",
        "name",
        "created_by",
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            _("General"),
            {"fields": ("name",)},
        ),
        (
            _("Connected Users"),
            {"fields": ("created_by",)},
        ),
        (
            _("Important dates"),
            {"fields": ("created_at", "updated_at")},
        ),
    )
    readonly_fields = [
        "uuid",
        "created_by",
        "created_at",
        "updated_at",
    ]


admin.site.register(CodeSpace, CodeSpaceAdmin)
admin.site.register(User, UserAdmin)
