from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from django.views.static import serve as static_serve

urlpatterns = [
    path("admin/", admin.site.urls),
    # The home page is the project list.
    path("", RedirectView.as_view(url="/projects/list/", permanent=False)),
    path("projects/", include("projects.urls")),
    path("users/", include("users.urls")),
    # User-uploaded media (avatars). Static files are served by WhiteNoise
    # in production and by the staticfiles app in development.
    re_path(
        r"^media/(?P<path>.*)$",
        static_serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
