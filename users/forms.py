import re
from urllib.parse import urlparse

from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError

from users import constants
from users.models import User


def validate_github_url(url):
    """Ensure a (already well-formed) URL points to github.com."""
    if not url:
        return url
    host = urlparse(url).netloc.lower().split("@")[-1].split(":")[0]
    if host not in constants.GITHUB_ALLOWED_HOSTS:
        raise ValidationError(constants.GITHUB_ERROR)
    return url


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


class EditProfileForm(forms.ModelForm):
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

    def clean_github_url(self):
        return validate_github_url((self.cleaned_data.get("github_url") or "").strip())


class ChangePasswordForm(PasswordChangeForm):
    """Password change form (old_password, new_password1, new_password2)."""

    # Django's PasswordChangeForm already exposes exactly the three fields the
    # template expects; subclassing keeps a project-specific name/hook point.
