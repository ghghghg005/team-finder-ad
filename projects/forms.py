from django import forms
from projects import constants
from projects.models import Project
from users.mixins import GithubUrlMixin

class ProjectForm(GithubUrlMixin, forms.ModelForm):
    """Create/edit form: name, description, github_url, status."""

    status = forms.ChoiceField(
        label="Статус",
        choices=constants.STATUS_CHOICES,   # вместо STATUS_FORM_CHOICES
        widget=forms.Select,
    )

    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]

    # clean_github_url удалён — теперь он в миксине GithubUrlMixin