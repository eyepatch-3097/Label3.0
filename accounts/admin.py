from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Org, User, OrgJoinRequest


@admin.register(Org)
class OrgAdmin(admin.ModelAdmin):
    list_display = ("name", "domain", "org_code", "created_at", "user_count")
    search_fields = ("name", "domain", "org_code")
    readonly_fields = ("org_code", "created_at")
    ordering = ("name",)

    def user_count(self, obj):
        return obj.users.count()
    user_count.short_description = "Users"


class UserAdmin(BaseUserAdmin):
    """
    Custom admin for our email-based User model.
    """
    ordering = ("email",)
    list_display = (
        "email",
        "org",
        "role",
        "status",
        "user_code",
        "is_staff",
        "is_superuser",
        "last_login",
        "date_joined",
    )
    list_filter = ("role", "status", "is_staff", "is_superuser", "org")
    search_fields = ("email", "user_code")
    readonly_fields = ("user_code", "date_joined", "last_login")

    # We removed username, so define fieldsets using email instead
    fieldsets = (
        ("Login Info", {"fields": ("email", "password")}),
        ("Organisation & Role", {"fields": ("org", "role", "status", "user_code")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "org", "role", "status", "is_staff", "is_superuser"),
        }),
    )

    filter_horizontal = ("groups", "user_permissions")


admin.site.register(User, UserAdmin)


@admin.register(OrgJoinRequest)
class OrgJoinRequestAdmin(admin.ModelAdmin):
    list_display = ("org", "user", "is_approved", "created_at")
    list_filter = ("is_approved", "org")
    search_fields = ("user__email", "org__name")
    readonly_fields = ("created_at",)
