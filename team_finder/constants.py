"""Project-wide constants for the team_finder configuration package."""

# Separator used to read list-like values from environment variables.
ENV_LIST_SEPARATOR = ","

# Default hosts used when DJANGO_ALLOWED_HOSTS is not provided via the environment.
DEFAULT_ALLOWED_HOSTS = "localhost,127.0.0.1"

# Where unauthenticated users are redirected from login-protected pages.
LOGIN_URL = "/users/login/"

# Default template variant (TeamFinder ships three template sets: 1, 2 and 3).
DEFAULT_TASK_VERSION = "1"
