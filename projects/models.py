from django.conf import settings
from django.db import models

from projects import constants


class Project(models.Model):
    """A pet-project published on the platform."""

    name = models.CharField("Название", max_length=constants.NAME_MAX_LENGTH)
    description = models.TextField("Описание", blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    github_url = models.URLField("GitHub", blank=True)
    status = models.CharField(
        "Статус",
        max_length=constants.STATUS_MAX_LENGTH,
        choices=constants.STATUS_CHOICES,
        default=constants.STATUS_OPEN,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="Участники",
        related_name="participated_projects",
        blank=True,
    )

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.name

    @property
    def is_open(self):
        return self.status == constants.STATUS_OPEN
