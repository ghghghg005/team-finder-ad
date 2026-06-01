"""Populate the database with demo users and projects.

Idempotent: running it more than once will not create duplicates. Useful for
reviewers who want sample data to click through the site.

    python manage.py seed_demo
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from projects.constants import STATUS_CLOSED, STATUS_OPEN
from projects.models import Project

User = get_user_model()

# email -> profile data
DEMO_USERS = [
    {
        "email": "maria@yandex.ru",
        "name": "Мария",
        "surname": "Иванова",
        "password": "password",
        "phone": "+79001112233",
        "github_url": "https://github.com/maria",
        "about": "Fullstack-разработчица, люблю Django и хорошие интерфейсы.",
    },
    {
        "email": "ivan@yandex.ru",
        "name": "Иван",
        "surname": "Петров",
        "password": "password123",
        "phone": "+79002223344",
        "github_url": "https://github.com/ivanpetrov",
        "about": "Backend-разработчик. Python, PostgreSQL, немного DevOps.",
    },
    {
        "email": "olga@yandex.ru",
        "name": "Ольга",
        "surname": "Смирнова",
        "password": "password123",
        "phone": "+79003334455",
        "github_url": "https://github.com/olgasmirnova",
        "about": "UI/UX дизайнер, ищу команду для pet-проектов.",
    },
    {
        "email": "pavel@yandex.ru",
        "name": "Павел",
        "surname": "Кузнецов",
        "password": "password123",
        "phone": "+79004445566",
        "github_url": "",
        "about": "Frontend на React, изучаю TypeScript.",
    },
]

# owner email -> list of projects
DEMO_PROJECTS = {
    "maria@yandex.ru": [
        {
            "name": "TeamFinder",
            "description": "Платформа для поиска единомышленников для pet-проектов.",
            "status": STATUS_OPEN,
            "github_url": "https://github.com/maria/teamfinder",
        },
        {
            "name": "Книжный клуб онлайн",
            "description": "Сервис для совместного чтения и обсуждения книг.",
            "status": STATUS_OPEN,
            "github_url": "",
        },
    ],
    "ivan@yandex.ru": [
        {
            "name": "API-шлюз для микросервисов",
            "description": "Лёгкий шлюз с аутентификацией и rate-limit.",
            "status": STATUS_OPEN,
            "github_url": "https://github.com/ivanpetrov/gateway",
        },
    ],
    "olga@yandex.ru": [
        {
            "name": "Дизайн-система TeamUI",
            "description": "Открытая дизайн-система с компонентами и токенами.",
            "status": STATUS_CLOSED,
            "github_url": "",
        },
    ],
    "pavel@yandex.ru": [
        {
            "name": "Погодный дашборд",
            "description": "Небольшой дашборд с прогнозом погоды на React.",
            "status": STATUS_OPEN,
            "github_url": "",
        },
    ],
}

SUPERUSER = {
    "email": "admin@teamfinder.local",
    "name": "Админ",
    "surname": "Админов",
    "password": "admin",
}


class Command(BaseCommand):
    help = "Create demo users, projects, participants and favorites."

    @transaction.atomic
    def handle(self, *args, **options):
        users = {}
        for data in DEMO_USERS:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "name": data["name"],
                    "surname": data["surname"],
                    "phone": data["phone"],
                    "github_url": data["github_url"],
                    "about": data["about"],
                },
            )
            if created:
                user.set_password(data["password"])
                user.save()
                self.stdout.write(f"  + user {user.email}")
            users[data["email"]] = user

        projects = []
        for owner_email, project_list in DEMO_PROJECTS.items():
            owner = users[owner_email]
            for data in project_list:
                project, created = Project.objects.get_or_create(
                    name=data["name"],
                    owner=owner,
                    defaults={
                        "description": data["description"],
                        "status": data["status"],
                        "github_url": data["github_url"],
                    },
                )
                # The owner is always a participant of their own project.
                project.participants.add(owner)
                projects.append(project)
                if created:
                    self.stdout.write(f"  + project «{project.name}» ({owner.email})")

        # A few cross-links so the user filters and favorites have data.
        maria = users["maria@yandex.ru"]
        ivan = users["ivan@yandex.ru"]
        olga = users["olga@yandex.ru"]
        pavel = users["pavel@yandex.ru"]

        teamfinder = Project.objects.filter(name="TeamFinder", owner=maria).first()
        gateway = Project.objects.filter(name="API-шлюз для микросервисов").first()
        if teamfinder:
            teamfinder.participants.add(ivan, olga)
            pavel.favorites.add(teamfinder)
            ivan.favorites.add(teamfinder)
        if gateway:
            gateway.participants.add(maria)
            maria.favorites.add(gateway)

        admin, created = User.objects.get_or_create(
            email=SUPERUSER["email"],
            defaults={
                "name": SUPERUSER["name"],
                "surname": SUPERUSER["surname"],
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password(SUPERUSER["password"])
            admin.save()
            self.stdout.write(f"  + superuser {admin.email}")

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
        self.stdout.write(
            "  Test account:  maria@yandex.ru / password\n"
            "  Admin account: admin@teamfinder.local / admin"
        )
