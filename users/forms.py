import re
from urllib.parse import urlparse

from django import forms
from django.contrib.auth.forms import PasswordChangeForm, ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from users import constants
from users.models import User
from users.mixins import GithubUrlMixin


class RegisterForm(forms.ModelForm):
    """Registration form: name, surname, email, password."""

    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """Authentication form: email + password."""

    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)


class EditProfileForm(GithubUrlMixin, forms.ModelForm):
    """Profile editing form with phone and GitHub validation."""

    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        if not phone:
            return phone

        if not re.match(constants.PHONE_INPUT_PATTERN, phone):
            raise ValidationError(constants.PHONE_ERROR_FORMAT)

        # Normalise to the canonical +7XXXXXXXXXX form.
        last_ten = phone[-10:]
        canonical = constants.PHONE_CANONICAL_PREFIX + last_ten
        legacy = constants.PHONE_LEADING_EIGHT + last_ten

        # Uniqueness across users, regardless of which format is stored.
        duplicates = User.objects.filter(
            phone__in=[canonical, legacy]
        ).exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise ValidationError(constants.PHONE_ERROR_UNIQUE)

        return canonical


class ChangePasswordForm(PasswordChangeForm):
    """Password change form (old_password, new_password1, new_password2)."""

    # Django's PasswordChangeForm already exposes exactly the three fields the
    # template expects; subclassing keeps a project-specific name/hook point.


class AdminUserCreationForm(forms.ModelForm):
    """Admin form to create a user with a properly hashed password."""
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Подтверждение пароля", widget=forms.PasswordInput)

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
