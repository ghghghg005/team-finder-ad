"""Constants for the users app."""

# --- Model field limits ---------------------------------------------------
NAME_MAX_LENGTH = 124
SURNAME_MAX_LENGTH = 124
PHONE_MAX_LENGTH = 12
ABOUT_MAX_LENGTH = 256

# --- Avatars --------------------------------------------------------------
AVATAR_UPLOAD_DIR = "avatars/"
AVATAR_SIZE = 256  # px, square
AVATAR_TEXT_COLOR = (255, 255, 255)
# A palette of calm, well-balanced background colours. White text stays
# readable on every one of them while none of them is harshly contrasting.
AVATAR_BACKGROUND_COLORS = [
    (94, 124, 159),   # muted blue
    (108, 142, 104),  # sage green
    (159, 116, 116),  # dusty rose
    (130, 118, 156),  # soft violet
    (176, 137, 104),  # warm sand
    (94, 148, 148),   # teal
    (150, 120, 140),  # mauve
    (120, 130, 150),  # slate
    (140, 150, 110),  # olive
    (110, 140, 160),  # steel blue
]
AVATAR_FONT_PATH = "fonts/Neue_Haas_Grotesk_Display_Pro_75_Bold.otf"
AVATAR_FONT_RATIO = 0.5  # font size relative to the avatar side
AVATAR_FALLBACK_LETTER = "?"

# --- Phone validation -----------------------------------------------------
# Accepted input formats: 8XXXXXXXXXX or +7XXXXXXXXXX (X is a digit).
PHONE_INPUT_PATTERN = r"^(?:8|\+7)\d{10}$"
PHONE_CANONICAL_PREFIX = "+7"
PHONE_LEADING_EIGHT = "8"
PHONE_ERROR_FORMAT = (
    "Введите номер в формате 8XXXXXXXXXX или +7XXXXXXXXXX."
)
PHONE_ERROR_UNIQUE = "Этот номер телефона уже используется другим пользователем."

# --- GitHub url validation ------------------------------------------------
GITHUB_ALLOWED_HOSTS = ("github.com", "www.github.com")
GITHUB_ERROR = "Ссылка должна вести на github.com."

# --- Auth / forms ---------------------------------------------------------
LOGIN_ERROR = "Неверный имейл или пароль."

# --- Pagination -----------------------------------------------------------
USERS_PER_PAGE = 12

# --- User list filters (variant 1) ---------------------------------------
FILTER_FAVORITE_OWNERS = "owners-of-favorite-projects"
FILTER_PARTICIPATING_OWNERS = "owners-of-participating-projects"
FILTER_INTERESTED_IN_MINE = "interested-in-my-projects"
FILTER_PARTICIPANTS_OF_MINE = "participants-of-my-projects"
ALLOWED_USER_FILTERS = (
    FILTER_FAVORITE_OWNERS,
    FILTER_PARTICIPATING_OWNERS,
    FILTER_INTERESTED_IN_MINE,
    FILTER_PARTICIPANTS_OF_MINE,
)
