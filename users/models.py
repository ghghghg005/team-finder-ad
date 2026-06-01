from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from users import constants
from users.managers import UserManager
from users.utils import generate_avatar


class User(AbstractBaseUser, PermissionsMixin):
    """Platform user identified by email.

    ``phone`` is stored as a (normalised) string and is intentionally allowed to
    be blank because registration only collects name/surname/email/password;
    the field is filled in later from the profile-editing page, where its
    format and uniqueness are validated.
    """

    email = models.EmailField("Email", unique=True)
    name = models.CharField("Имя", max_length=constants.NAME_MAX_LENGTH)
    surname = models.CharField("Фамилия", max_length=constants.SURNAME_MAX_LENGTH)
    avatar = models.ImageField("Аватар", upload_to=constants.AVATAR_UPLOAD_DIR)
    phone = models.CharField(
        "Телефон", max_length=constants.PHONE_MAX_LENGTH, blank=True
    )
    github_url = models.URLField("GitHub", blank=True)
    about = models.TextField(
        "О себе", max_length=constants.ABOUT_MAX_LENGTH, blank=True
    )
    is_active = models.BooleanField("Активен", default=True)
    is_staff = models.BooleanField("Администратор", default=False)

    # Variant 1: projects the user marked as favorite.
    favorites = models.ManyToManyField(
        "projects.Project",
        verbose_name="Избранное",
        related_name="interested_users",
        blank=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["surname", "name"]   # исправлено

    def __str__(self):
        return f"{self.name} {self.surname} <{self.email}>"

    def get_full_name(self):
        return f"{self.name} {self.surname}".strip()

    def get_short_name(self):
        return self.name

    def save(self, *args, **kwargs):
        # Generate the initial avatar (first letter on a solid background)
        # before the very first save, as required by the specification.
        if not self.avatar:
            self.avatar = generate_avatar(self.name)
        super().save(*args, **kwargs)
