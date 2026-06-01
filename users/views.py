from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from users import constants
from users.forms import (
    ChangePasswordForm,
    EditProfileForm,
    LoginForm,
    RegisterForm,
)
from users.models import User

MODEL_BACKEND = "django.contrib.auth.backends.ModelBackend"


def register(request):
    """Sign up, log the new user in and send them to the home page."""
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user, backend=MODEL_BACKEND)
        return redirect("projects:list")
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    """Authenticate by email + password."""
    form = LoginForm(request.POST or None)
    if form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )
        if user is not None:
            login(request, user)
            return redirect("projects:list")
        form.add_error(None, constants.LOGIN_ERROR)
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    """Log the user out and return to the home page."""
    logout(request)
    return redirect("projects:list")


def user_details(request, user_id):
    """Public profile page."""
    profile = get_object_or_404(User, pk=user_id)
    return render(request, "users/user-details.html", {"user": profile})


def _filter_users(me, key, users):
    """Apply one of the four predefined variant-1 user filters."""
    if key == constants.FILTER_FAVORITE_OWNERS:
        return users.filter(owned_projects__in=me.favorites.all())
    if key == constants.FILTER_PARTICIPATING_OWNERS:
        return users.filter(owned_projects__in=me.participated_projects.all())
    if key == constants.FILTER_INTERESTED_IN_MINE:
        return users.filter(favorites__owner=me)
    if key == constants.FILTER_PARTICIPANTS_OF_MINE:
        return users.filter(participated_projects__owner=me)
    return users


def users_list(request):
    """All users (ordered by id), optionally filtered, paginated by 12."""
    users = User.objects.all()
    active_filter = request.GET.get("filter")
    if request.user.is_authenticated and active_filter in constants.ALLOWED_USER_FILTERS:
        users = _filter_users(request.user, active_filter, users).distinct()
    else:
        active_filter = None

    paginator = Paginator(users, constants.USERS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    query_prefix = f"filter={active_filter}&" if active_filter else ""
    return render(
        request,
        "users/participants.html",
        {
            "participants": users,
            "page_obj": page_obj,
            "active_filter": active_filter,
            "query_prefix": query_prefix,
        },
    )


@login_required
def edit_profile(request):
    """Edit the current user's general information."""
    form = EditProfileForm(
        request.POST or None, request.FILES or None, instance=request.user
    )
    if form.is_valid():
        form.save()
        return redirect("users:detail", user_id=request.user.id)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    """Change the current user's password."""
    form = ChangePasswordForm(user=request.user, data=request.POST or None)
    if form.is_valid():
        form.save()
        update_session_auth_hash(request, form.user)
        return redirect("users:detail", user_id=request.user.id)
    return render(request, "users/change_password.html", {"form": form})
