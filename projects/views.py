from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.db.models import Count
from http import HTTPStatus

from projects import constants
from projects.forms import ProjectForm
from projects.models import Project
from projects.service import auth_required_json, paginate


def project_list(request):
    """Home page: all projects, newest first, paginated by PROJECTS_PER_PAGE (12)."""
    projects = (Project.objects
                .select_related("owner")
                .prefetch_related("participants")
                .annotate(participants_count=Count("participants"))
                .order_by("-created_at"))
    page_obj = paginate(projects, request, constants.PROJECTS_PER_PAGE)
    return render(
        request,
        "projects/project_list.html",
        {"projects": projects, "page_obj": page_obj, "query_prefix": ""},
    )


@login_required
def favorite_projects(request):
    """Favorites page: projects the current user marked as favorite."""
    projects = (request.user.favorites
                .select_related("owner")
                .prefetch_related("participants")
                .annotate(participants_count=Count("participants"))
                .order_by("-created_at"))
    return render(
        request, "projects/favorite_projects.html", {"projects": projects}
    )


def project_details(request, project_id):
    """Detailed project page."""
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        pk=project_id
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project(request):
    """Create a new project; the author also becomes a participant."""
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect("projects:detail", project_id=project.id)
    return render(
        request, "projects/create-project.html", {"form": form, "is_edit": False}
    )


@login_required
def edit_project(request, project_id):
    """Edit an existing project (owner or admin only)."""
    project = get_object_or_404(Project, pk=project_id)
    if request.user != project.owner and not request.user.is_staff:
        return HttpResponseForbidden("Недостаточно прав для редактирования проекта.")

    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect("projects:detail", project_id=project.id)
    return render(
        request, "projects/create-project.html", {"form": form, "is_edit": True}
    )


@require_POST
def toggle_favorite(request, project_id):
    """Add/remove a project from the current user's favorites (AJAX)."""
    if not request.user.is_authenticated:
        return auth_required_json()

    project = get_object_or_404(Project, pk=project_id)
    if (favorited := request.user.favorites.filter(pk=project.pk).exists()):
        request.user.favorites.remove(project)
        favorited = False
    else:
        request.user.favorites.add(project)
        favorited = True
    return JsonResponse({"status": constants.STATUS_OK, "favorited": favorited})


@require_POST
def complete_project(request, project_id):
    """Mark an open project as closed (owner or admin only)."""
    if not request.user.is_authenticated:
        return auth_required_json()

    project = get_object_or_404(Project, pk=project_id)
    if request.user != project.owner and not request.user.is_staff:
        return JsonResponse(
            {"status": "error", "detail": "Недостаточно прав."},
            status=HTTPStatus.FORBIDDEN
        )
    if project.status != constants.STATUS_OPEN:
        return JsonResponse(
            {"status": "error", "detail": "Проект уже закрыт."},
            status=HTTPStatus.BAD_REQUEST
        )

    project.status = constants.STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse(
        {"status": constants.STATUS_OK, "project_status": constants.STATUS_CLOSED}
    )


@require_POST
def toggle_participate(request, project_id):
    """Join/leave a project as a participant (AJAX)."""
    if not request.user.is_authenticated:
        return auth_required_json()

    project = get_object_or_404(Project, pk=project_id)
    if (participant := project.participants.filter(pk=request.user.pk).exists()):
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True
    return JsonResponse({"status": constants.STATUS_OK, "participant": participant})