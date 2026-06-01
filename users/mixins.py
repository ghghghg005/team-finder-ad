from django import forms
from users.validators import validate_github_url


class GithubUrlMixin(forms.ModelForm):
    def clean_github_url(self):
        return validate_github_url((self.cleaned_data.get("github_url") or "").strip())
