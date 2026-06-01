from django.contrib import admin
from users.models import User
from users.forms import AdminUserCreationForm, AdminUserChangeForm


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = AdminUserCreationForm
    form = AdminUserChangeForm
    model = User

    list_display = ("id", "email", "name", "surname", "is_staff", "is_active")
    list_display_links = ("id", "email")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("email", "name", "surname")
    ordering = ("id",)
    filter_horizontal = ("groups", "user_permissions", "favorites")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Личная информация", {
            "fields": ("name", "surname", "avatar", "phone", "github_url", "about"),
        }),
        ("Избранное", {"fields": ("favorites",)}),
        ("Права доступа", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
        }),
        ("Важные даты", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "name", "surname", "password1", "password2"),
        }),
    )
