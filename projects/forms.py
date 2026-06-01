from urllib.parse import urlparse

from django import forms
from django.core.exceptions import ValidationError

from projects import constants
from projects.models import Project


class ProjectForm(forms.ModelForm):
    """Create/edit form: name, description, github_url, status."""

    status = forms.ChoiceField(
        label="Статус",
        choices=constants.STATUS_FORM_CHOICES,
        widget=forms.Select,
    )

    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]

    def clean_github_url(self):
        url = (self.cleaned_data.get("github_url") or "").strip()
        if not url:
            return url
        host = urlparse(url).netloc.lower().split("@")[-1].split(":")[0]
        if host not in constants.GITHUB_ALLOWED_HOSTS:
            raise ValidationError(constants.GITHUB_ERROR)
        return url
