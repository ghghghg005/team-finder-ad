from http import HTTPStatus
from django.core.paginator import Paginator
from django.http import JsonResponse

def auth_required_json():
    return JsonResponse(
        {"status": "error", "detail": "Требуется авторизация."},
        status=HTTPStatus.FORBIDDEN
    )


def paginate(queryset, request, per_page):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("page"))