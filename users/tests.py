import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from projects.models import Project
from users import constants

User = get_user_model()
TEMP_MEDIA = tempfile.mkdtemp()


def make_user(email, name="Тест", surname="Тестов", password="password123"):
    return User.objects.create_user(
        email=email, name=name, surname=surname, password=password
    )


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class UserModelTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)
        super().tearDownClass()

    def test_create_user(self):
        user = make_user("a@example.com")
        self.assertTrue(user.check_password("password123"))
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email="admin@example.com", name="A", surname="B", password="x"
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_email_is_username_field(self):
        self.assertEqual(User.USERNAME_FIELD, "email")

    def test_avatar_is_generated_on_create(self):
        user = make_user("avatar@example.com", name="Дмитрий")
        self.assertTrue(user.avatar)
        self.assertTrue(user.avatar.name.endswith(".png"))


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class AuthViewTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)
        super().tearDownClass()

    def test_register_get(self):
        response = self.client.get(reverse("users:register"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_register_creates_user_logs_in_and_redirects(self):
        response = self.client.post(
            reverse("users:register"),
            {"name": "Иван", "surname": "Иванов",
             "email": "new@example.com", "password": "strongpass123"},
        )
        self.assertRedirects(
            response, reverse("projects:list")
        )
        self.assertTrue(User.objects.filter(email="new@example.com").exists())
        # auto-login: the session carries an authenticated user
        self.assertIn("_auth_user_id", self.client.session)

    def test_register_duplicate_email_invalid(self):
        make_user("dupe@example.com")
        response = self.client.post(
            reverse("users:register"),
            {"name": "X", "surname": "Y",
             "email": "dupe@example.com", "password": "strongpass123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)

    def test_login_valid(self):
        make_user("login@example.com", password="mypassword1")
        response = self.client.post(
            reverse("users:login"),
            {"email": "login@example.com", "password": "mypassword1"},
        )
        self.assertRedirects(
            response, reverse("projects:list")
        )

    def test_login_invalid_shows_error(self):
        make_user("login2@example.com", password="mypassword1")
        response = self.client.post(
            reverse("users:login"),
            {"email": "login2@example.com", "password": "wrong"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, constants.LOGIN_ERROR)

    def test_logout_redirects_home(self):
        user = make_user("logout@example.com")
        self.client.force_login(user)
        response = self.client.get(reverse("users:logout"))
        self.assertRedirects(
            response, reverse("projects:list")
        )
        self.assertNotIn("_auth_user_id", self.client.session)


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class ProfileViewTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = make_user("me@example.com", name="Пётр")

    def test_user_details_renders_profile(self):
        response = self.client.get(reverse("users:detail", args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["user"], self.user)
        self.assertContains(response, "Пётр")

    def test_edit_profile_requires_login(self):
        response = self.client.get(reverse("users:edit-profile"))
        self.assertEqual(response.status_code, 302)

    def test_edit_profile_normalizes_phone(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("users:edit-profile"),
            {"name": "Пётр", "surname": "Петров", "about": "",
             "phone": "89001234567", "github_url": ""},
        )
        self.assertRedirects(
            response, reverse("users:detail", args=[self.user.id]),
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, "+79001234567")

    def test_edit_profile_rejects_bad_phone(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("users:edit-profile"),
            {"name": "Пётр", "surname": "Петров", "about": "",
             "phone": "12345", "github_url": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("phone", response.context["form"].errors)

    def test_edit_profile_rejects_duplicate_phone_cross_format(self):
        other = make_user("other@example.com")
        other.phone = "+79001234567"
        other.save()
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("users:edit-profile"),
            {"name": "Пётр", "surname": "Петров", "about": "",
             "phone": "89001234567", "github_url": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("phone", response.context["form"].errors)

    def test_edit_profile_rejects_non_github_url(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("users:edit-profile"),
            {"name": "Пётр", "surname": "Петров", "about": "",
             "phone": "", "github_url": "https://gitlab.com/me"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("github_url", response.context["form"].errors)

    def test_change_password(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("users:change-password"),
            {"old_password": "password123",
             "new_password1": "brandNewPass123",
             "new_password2": "brandNewPass123"},
        )
        self.assertRedirects(
            response, reverse("users:detail", args=[self.user.id]),
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("brandNewPass123"))


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class UsersListTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.me = make_user("me@example.com", name="Я")
        self.author = make_user("author@example.com", name="Автор")
        self.participant = make_user("part@example.com", name="Участник")
        self.fan = make_user("fan@example.com", name="Фанат")

    def test_users_list_orders_by_id_and_paginates(self):
        for i in range(15):
            make_user(f"u{i}@example.com")
        response = self.client.get(reverse("users:list"))
        self.assertEqual(response.status_code, 200)
        page = response.context["page_obj"]
        self.assertEqual(len(page.object_list), constants.USERS_PER_PAGE)
        ids = [u.id for u in page.object_list]
        self.assertEqual(ids, sorted(ids))

    def test_filter_ignored_for_anonymous(self):
        response = self.client.get(
            reverse("users:list") + "?filter=" + constants.FILTER_FAVORITE_OWNERS
        )
        self.assertIsNone(response.context["active_filter"])

    def test_filter_owners_of_favorite_projects(self):
        project = Project.objects.create(name="P", owner=self.author)
        self.me.favorites.add(project)
        self.client.force_login(self.me)
        response = self.client.get(
            reverse("users:list") + "?filter=" + constants.FILTER_FAVORITE_OWNERS
        )
        self.assertEqual(list(response.context["page_obj"].object_list), [self.author])

    def test_filter_owners_of_participating_projects(self):
        project = Project.objects.create(name="P", owner=self.author)
        project.participants.add(self.me)
        self.client.force_login(self.me)
        response = self.client.get(
            reverse("users:list") + "?filter="
            + constants.FILTER_PARTICIPATING_OWNERS
        )
        self.assertEqual(list(response.context["page_obj"].object_list), [self.author])

    def test_filter_interested_in_my_projects(self):
        project = Project.objects.create(name="P", owner=self.me)
        self.fan.favorites.add(project)
        self.client.force_login(self.me)
        response = self.client.get(
            reverse("users:list") + "?filter=" + constants.FILTER_INTERESTED_IN_MINE
        )
        self.assertEqual(list(response.context["page_obj"].object_list), [self.fan])

    def test_filter_participants_of_my_projects(self):
        project = Project.objects.create(name="P", owner=self.me)
        project.participants.add(self.participant)
        self.client.force_login(self.me)
        response = self.client.get(
            reverse("users:list") + "?filter="
            + constants.FILTER_PARTICIPANTS_OF_MINE
        )
        self.assertEqual(
            list(response.context["page_obj"].object_list), [self.participant]
        )
