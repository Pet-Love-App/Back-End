from django.db.models import Q
from django.http import JsonResponse

from .models import Additive, Ingredient


# Create your views here.
def search_additive(request):
    """
    按名字搜索添加剂
    """
    if request.method == "GET":
        query = request.GET.get("name", "").strip()

        if not query:
            return JsonResponse({"error": "请提供搜索关键词"}, status=400)

        try:
            additive = Additive.objects.get(Q(name=query) | Q(en_name=query))
            return JsonResponse(
                {
                    "query": query,
                    "additive": {
                        "id": additive.id,
                        "name": additive.name,
                        "en_name": additive.en_name,
                        "applicable_range": additive.applicable_range,
                        "type": additive.type,
                    },
                },
                status=200,
            )
        except Additive.DoesNotExist:
            return JsonResponse({"error": "目标不在数据库中"}, status=404)

    return JsonResponse({"error": "只支持GET请求"}, status=405)


def search_ingredient(request):
    """
    按名字搜索成分
    """
    if request.method == "GET":
        query = request.GET.get("name", "").strip()

        if not query:
            return JsonResponse({"error": "请提供搜索关键词"}, status=400)

        try:
            ingredient = Ingredient.objects.get(Q(name=query) | Q(label=query))
            return JsonResponse(
                {
                    "query": query,
                    "ingredient": {
                        "id": ingredient.id,
                        "name": ingredient.name,
                        "type": ingredient.type,
                        "label": ingredient.label,
                        "desc": ingredient.desc,
                    },
                },
                status=200,
            )
        except Ingredient.DoesNotExist:
            return JsonResponse({"error": "目标不在数据库中"}, status=404)

    return JsonResponse({"error": "只支持GET请求"}, status=405)
