# TeamFinder — бэкенд (Вариант 1)

Платформа, на которой разработчики, дизайнеры и другие специалисты находят
единомышленников для совместной работы над pet-проектами: публикуют идеи,
собирают команду и откликаются на предложения.

Бэкенд написан на **Django**, данные хранятся в **PostgreSQL**.
Реализован **Вариант 1**: «Избранное» и фильтрация пользователей.

---

## Стек

- Python 3.12, Django 5.2
- PostgreSQL 16
- Gunicorn + WhiteNoise (продакшн)
- Pillow (генерация аватаров)
- Docker / Docker Compose

---

## Быстрый старт через Docker Compose (рекомендуется)

Поднимается весь проект целиком: PostgreSQL и Django-приложение.

```bash
# 1. Создайте .env на основе примера
cp .env_example .env

# 2. Соберите и запустите контейнеры
docker compose up -d --build
```

При старте контейнера автоматически выполняются:
миграции → сборка статики (`collectstatic`) → наполнение демо-данными (`seed_demo`).

Приложение будет доступно по адресу **http://localhost:8000**,
админка — **http://localhost:8000/admin/**.

Данные PostgreSQL, загруженные медиафайлы и собранная статика хранятся
в именованных volumes (`postgres_data`, `media_data`, `static_data`)
и не теряются при перезапуске контейнеров.

Остановить:

```bash
docker compose down        # остановить, данные сохраняются в volumes
docker compose down -v     # остановить и удалить данные
```

> Если порт `5432` или `8000` уже занят на вашей машине, поменяйте левую часть
> в `ports` соответствующего сервиса в `docker-compose.yml`.

---

## Локальный запуск (без Docker, для разработки)

```bash
# 1. Виртуальное окружение
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Зависимости
pip install -r requirements.txt

# 3. .env
cp .env_example .env
```

Дальше есть два варианта базы данных:

**A. SQLite (быстро, без отдельной БД).** В `.env` поставьте `USE_SQLITE=True`, затем:

```bash
python manage.py migrate
python manage.py seed_demo        # демо-пользователи и проекты
python manage.py runserver
```

**B. PostgreSQL.** Запустите только базу из docker-compose и оставьте `USE_SQLITE=False`:

```bash
docker compose up -d db
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Создать собственного суперпользователя:

```bash
python manage.py createsuperuser   # спросит email, имя, фамилию, пароль
```

---

## Тестовые аккаунты

Команда `seed_demo` создаёт несколько пользователей (у каждого есть хотя бы
один проект) и одного администратора:

| Роль          | Email                     | Пароль     |
|---------------|---------------------------|------------|
| Пользователь  | `maria@yandex.ru`         | `password` |
| Пользователь  | `ivan@yandex.ru`          | `password123` |
| Пользователь  | `olga@yandex.ru`          | `password123` |
| Пользователь  | `pavel@yandex.ru`         | `password123` |
| Администратор | `admin@teamfinder.local`  | `admin`    |

---

## Тесты и линтер

```bash
python manage.py test     # 43 теста (модели, формы, view, права доступа, фильтры)
flake8 .                  # PEP8, max-line-length = 100
```

В CI (GitHub Actions, `.github/workflows/ci.yml`) на каждый push/PR
запускаются flake8, проверка миграций и тесты на PostgreSQL.

---

## Структура

```
team_finder/      # настройки проекта, корневые urls, constants.py
users/            # модель User, регистрация/вход, профиль, смена пароля, список и фильтры
projects/         # модель Project, список/детали/избранное, создание и редактирование
templates_var1/   # HTML-шаблоны варианта 1
static/           # css, js, шрифты, аватар по умолчанию
```

### Приложения и модели

- **users** — кастомная модель `User` (вход по email, свой `UserManager`,
  автогенерация аватара). Поля: `email`, `name`, `surname`, `avatar`, `phone`,
  `github_url`, `about`, `is_active`, `is_staff`, а также `favorites`
  (M2M к `Project`, обратная связь `project.interested_users`).
- **projects** — модель `Project`: `name`, `description`, `owner`
  (FK, `user.owned_projects`), `created_at`, `github_url`, `status`
  (`open`/`closed`), `participants` (M2M, `user.participated_projects`).

Приложения самодостаточны: `users` ссылается на `Project` строкой
(`"projects.Project"`), а `projects` — через `settings.AUTH_USER_MODEL`.

---

## Принятые решения и отступления от формулировки

Эти пункты стоит учесть при ревью — где требования задания
противоречили друг другу, выбран более конкретный (технический) вариант.

1. **Вариант 1.** `TASK_VERSION=1`. Папки `templates_var2`/`templates_var3`
   в репозитории не используются (их можно удалить).
2. **Кастомная модель `User`** (`AUTH_USER_MODEL = "users.User"`),
   идентификатор — `email`. Добавлено поле `is_superuser` (через
   `PermissionsMixin`) — оно не указано в списке полей задания, но необходимо
   для работы админки и системы прав. Шаблоны его не используют.
3. **Аватар** генерируется в `User.save()` перед первым сохранением: первая
   буква имени белым цветом на однотонном фоне из спокойной палитры
   (`users/utils.py`).
4. **Телефон.** В модели `phone` допускает пустое значение (`blank=True`),
   потому что при регистрации собираются только имя, фамилия, email и пароль —
   телефон заполняется позже на странице редактирования профиля. Там же
   проверяется формат (`8XXXXXXXXXX` либо `+7XXXXXXXXXX`) и уникальность
   (в т.ч. между форматами `8…`/`+7…`); номер нормализуется к виду `+7XXXXXXXXXX`.
5. **Регистрация.** Согласно разделу «Форма регистрации», после успешной
   регистрации пользователь сразу авторизуется и перенаправляется на главную
   (`/projects/list/`). Это расходится с общей фразой «переадресовывается на
   страницу входа» — выбран явный технический сценарий из спецификации формы.
6. **Список пользователей** сортируется по `id` (по порядку добавления в БД),
   как указано в спецификации Варианта 1 для `/users/list/`.
7. **`ALLOWED_HOSTS`** читается из переменной окружения `DJANGO_ALLOWED_HOSTS`
   (строка делится по запятой), значение по умолчанию — `localhost,127.0.0.1`.
   Звёздочка `"*"` не используется.
8. **Константы** вынесены в `constants.py` (на уровне проекта и каждого приложения).
9. **View-формы** не проверяют `request.method == "POST"` вручную, а используют
   паттерн `Form(request.POST or None)` и проверку на валидность.
10. **Продакшн.** В контейнере приложение обслуживается Gunicorn, статика —
    через WhiteNoise (после `collectstatic`), медиа (аватары) — отдаются Django.
    В Docker `DEBUG=False`.
11. **Локальная разработка** может использовать SQLite (`USE_SQLITE=True`) —
    это лишь удобство для разработки; по умолчанию и в Docker используется
    PostgreSQL.
