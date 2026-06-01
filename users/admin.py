from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from users.models import User


class AdminUserCreationForm(forms.ModelForm):
    """Admin form to create a user with a properly hashed password."""

    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Подтверждение пароля", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("email", "name", "surname")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class AdminUserChangeForm(forms.ModelForm):
    """Admin form to edit a user; password is shown as a hash with a change link."""

    password = ReadOnlyPasswordHashField(
        label="Пароль",
        help_text=(
            "Пароли хранятся в зашифрованном виде. Изменить пароль можно "
            'по <a href="../password/">этой ссылке</a>.'
        ),
    )

    class Meta:
        model = User
        fields = "__all__"


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
