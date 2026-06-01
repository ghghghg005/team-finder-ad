"""Custom manager for the email-based User model."""

from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """Manager for a User model that uses email as the unique identifier."""

    use_in_migrations = True

    def _create_user(self, email, name, surname, password, **extra_fields):
        if not email:
            raise ValueError("Пользователь должен иметь адрес электронной почты.")
        if not name:
            raise ValueError("Пользователь должен иметь имя.")
        if not surname:
            raise ValueError("Пользователь должен иметь фамилию.")

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, name, surname, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, name, surname, password, **extra_fields)

    def create_superuser(self, email, name, surname, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self._create_user(email, name, surname, password, **extra_fields)
