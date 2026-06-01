"""Constants for the projects app."""

# --- Model field limits ---------------------------------------------------
NAME_MAX_LENGTH = 200
STATUS_MAX_LENGTH = 6

# --- Status ---------------------------------------------------------------
STATUS_OPEN = "open"
STATUS_CLOSED = "closed"
STATUS_CHOICES = [
    (STATUS_OPEN, "Открыт"),
    (STATUS_CLOSED, "Закрыт"),
]

# --- Pagination -----------------------------------------------------------
PROJECTS_PER_PAGE = 12

# --- GitHub url validation ------------------------------------------------
GITHUB_ALLOWED_HOSTS = ("github.com", "www.github.com")
GITHUB_ERROR = "Ссылка должна вести на github.com."

# --- JSON response keys/values -------------------------------------------
STATUS_OK = "ok"
