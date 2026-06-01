from urllib.parse import urlparse
from django.core.exceptions import ValidationError
from users import constants


def validate_github_url(url):
    """Ensure a (already well-formed) URL points to github.com."""
    if not url:
        return url
    host = urlparse(url).netloc.lower().split("@")[-1].split(":")[0]
    if host not in constants.GITHUB_ALLOWED_HOSTS:
        raise ValidationError(constants.GITHUB_ERROR)
    return url
