import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from projects.constants import STATUS_CLOSED, STATUS_OPEN
from projects.models import Project

User = get_user_model()
TEMP_MEDIA = tempfile.mkdtemp()


def make_user(email, name="Тест", surname="Тестов", password="password123"):
    return User.objects.create_user(
        email=email, name=name, surname=surname, password=password
    )


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class ProjectViewTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.owner = make_user("owner@example.com", name="Олег")
        self.other = make_user("other@example.com", name="Анна")

    def _make_project(self, name="Проект", owner=None, status=STATUS_OPEN):
        return Project.objects.create(
            name=name, owner=owner or self.owner, status=status
        )

    # --- home / list -----------------------------------------------------
    def test_root_redirects_to_project_list(self):
        response = self.client.get("/")
        self.assertRedirects(response, "/projects/list/")

    def test_project_list_paginates_by_12(self):
        for i in range(13):
            self._make_project(name=f"Проект {i}")
        response = self.client.get(reverse("projects:list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"].object_list), 12)
        page2 = self.client.get(reverse("projects:list") + "?page=2")
        self.assertEqual(len(page2.context["page_obj"].object_list), 1)

    def test_project_list_ordered_newest_first(self):
        old = self._make_project(name="Старый")
        new = self._make_project(name="Новый")
        response = self.client.get(reverse("projects:list"))
        ids = [p.id for p in response.context["page_obj"].object_list]
        self.assertEqual(ids, [new.id, old.id])

    def test_project_details_renders(self):
        project = self._make_project()
        response = self.client.get(reverse("projects:detail", args=[project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["project"], project)
        self.assertContains(response, project.name)

    # --- create ----------------------------------------------------------
    def test_create_requires_login(self):
        response = self.client.get(reverse("projects:create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_create_get_shows_form(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("projects:create"))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["is_edit"])

    def test_create_post_sets_owner_and_participant_and_redirects(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("projects:create"),
            {"name": "Новый проект", "description": "desc", "status": STATUS_OPEN,
             "github_url": ""},
        )
        project = Project.objects.get(name="Новый проект")
        self.assertRedirects(
            response, reverse("projects:detail", args=[project.id]),
        )
        self.assertEqual(project.owner, self.owner)
        self.assertIn(self.owner, project.participants.all())

    def test_create_invalid_github_url_rejected(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("projects:create"),
            {"name": "X", "description": "", "status": STATUS_OPEN,
             "github_url": "https://gitlab.com/foo"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Project.objects.filter(name="X").exists())

    def test_create_requires_name(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("projects:create"),
            {"name": "", "description": "", "status": STATUS_OPEN, "github_url": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)

    # --- edit ------------------------------------------------------------
    def test_edit_forbidden_for_non_owner(self):
        project = self._make_project()
        self.client.force_login(self.other)
        response = self.client.get(reverse("projects:edit", args=[project.id]))
        self.assertEqual(response.status_code, 403)

    def test_edit_updates_project(self):
        project = self._make_project()
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("projects:edit", args=[project.id]),
            {"name": "Изменён", "description": "new", "status": STATUS_CLOSED,
             "github_url": ""},
        )
        self.assertRedirects(
            response, reverse("projects:detail", args=[project.id]),
        )
        project.refresh_from_db()
        self.assertEqual(project.name, "Изменён")
        self.assertEqual(project.status, STATUS_CLOSED)

    # --- toggle favorite -------------------------------------------------
    def test_toggle_favorite_requires_auth(self):
        project = self._make_project()
        response = self.client.post(
            reverse("projects:toggle-favorite", args=[project.id])
        )
        self.assertEqual(response.status_code, 403)

    def test_toggle_favorite_adds_then_removes(self):
        project = self._make_project()
        self.client.force_login(self.other)
        url = reverse("projects:toggle-favorite", args=[project.id])

        response = self.client.post(url)
        self.assertEqual(response.json(), {"status": "ok", "favorited": True})
        self.assertIn(project, self.other.favorites.all())

        response = self.client.post(url)
        self.assertEqual(response.json(), {"status": "ok", "favorited": False})
        self.assertNotIn(project, self.other.favorites.all())

    def test_toggle_favorite_rejects_get(self):
        project = self._make_project()
        self.client.force_login(self.other)
        response = self.client.get(
            reverse("projects:toggle-favorite", args=[project.id])
        )
        self.assertEqual(response.status_code, 405)

    def test_favorites_page_lists_only_my_favorites(self):
        mine = self._make_project(name="Любимый")
        self._make_project(name="Чужой")
        self.client.force_login(self.other)
        self.other.favorites.add(mine)
        response = self.client.get(reverse("projects:favorites"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["projects"]), [mine])

    # --- complete --------------------------------------------------------
    def test_complete_by_owner_closes_project(self):
        project = self._make_project(status=STATUS_OPEN)
        self.client.force_login(self.owner)
        response = self.client.post(reverse("projects:complete", args=[project.id]))
        self.assertEqual(
            response.json(), {"status": "ok", "project_status": "closed"}
        )
        project.refresh_from_db()
        self.assertEqual(project.status, STATUS_CLOSED)

    def test_complete_forbidden_for_non_owner(self):
        project = self._make_project(status=STATUS_OPEN)
        self.client.force_login(self.other)
        response = self.client.post(reverse("projects:complete", args=[project.id]))
        self.assertEqual(response.status_code, 403)
        project.refresh_from_db()
        self.assertEqual(project.status, STATUS_OPEN)

    def test_complete_already_closed_is_bad_request(self):
        project = self._make_project(status=STATUS_CLOSED)
        self.client.force_login(self.owner)
        response = self.client.post(reverse("projects:complete", args=[project.id]))
        self.assertEqual(response.status_code, 400)

    # --- toggle participate ---------------------------------------------
    def test_toggle_participate_requires_auth(self):
        project = self._make_project()
        response = self.client.post(
            reverse("projects:toggle-participate", args=[project.id])
        )
        self.assertEqual(response.status_code, 403)

    def test_toggle_participate_joins_then_leaves(self):
        project = self._make_project()
        self.client.force_login(self.other)
        url = reverse("projects:toggle-participate", args=[project.id])

        response = self.client.post(url)
        self.assertEqual(response.json(), {"status": "ok", "participant": True})
        self.assertIn(self.other, project.participants.all())

        response = self.client.post(url)
        self.assertEqual(response.json(), {"status": "ok", "participant": False})
        self.assertNotIn(self.other, project.participants.all())
