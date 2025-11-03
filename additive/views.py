from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Additive, Ingredient


def search_additive(request):
    """
    按名字搜索添加剂
    支持精确匹配和模糊匹配
    """
    if request.method == "GET":
        query = request.GET.get("name", "").strip()
        fuzzy = request.GET.get("fuzzy", "false").lower() == "true"  # 是否启用模糊搜索

        if not query:
            return JsonResponse({"error": "请提供搜索关键词"}, status=400)

        # 1. 尝试精确匹配
        try:
            additive = Additive.objects.get(Q(name=query) | Q(en_name=query))
            return JsonResponse(
                {
                    "query": query,
                    "match_type": "exact",
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
            # 2. 如果精确匹配失败，尝试模糊匹配
            additives = Additive.objects.filter(
                Q(name__icontains=query) | Q(en_name__icontains=query)
            )

            if additives.exists():
                # 如果只有一个结果，直接返回
                if additives.count() == 1:
                    additive = additives.first()
                    return JsonResponse(
                        {
                            "query": query,
                            "match_type": "fuzzy_single",
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
                else:
                    # 多个结果：返回列表供用户选择
                    results = [
                        {
                            "id": a.id,
                            "name": a.name,
                            "en_name": a.en_name,
                            "applicable_range": a.applicable_range,
                            "type": a.type,
                        }
                        for a in additives[:10]  # 最多返回10个
                    ]
                    return JsonResponse(
                        {
                            "query": query,
                            "match_type": "fuzzy_multiple",
                            "count": additives.count(),
                            "additives": results,
                            "message": f"找到 {additives.count()} 个匹配结果",
                        },
                        status=200,
                    )
            else:
                return JsonResponse({"error": "目标不在数据库中"}, status=404)

    return JsonResponse({"error": "只支持GET请求"}, status=405)


def search_ingredient(request):
    """
    按名字搜索成分
    支持精确匹配和模糊匹配
    """
    if request.method == "GET":
        query = request.GET.get("name", "").strip()

        if not query:
            return JsonResponse({"error": "请提供搜索关键词"}, status=400)

        # 1. 尝试精确匹配
        try:
            ingredient = Ingredient.objects.get(Q(name=query) | Q(label=query))
            return JsonResponse(
                {
                    "query": query,
                    "match_type": "exact",
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
            # 2. 如果精确匹配失败，尝试模糊匹配
            ingredients = Ingredient.objects.filter(
                Q(name__icontains=query) | Q(label__icontains=query)
            )

            if ingredients.exists():
                # 如果只有一个结果，直接返回
                if ingredients.count() == 1:
                    ingredient = ingredients.first()
                    return JsonResponse(
                        {
                            "query": query,
                            "match_type": "fuzzy_single",
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
                else:
                    # 多个结果：返回列表供用户选择
                    results = [
                        {
                            "id": i.id,
                            "name": i.name,
                            "type": i.type,
                            "label": i.label,
                            "desc": i.desc,
                        }
                        for i in ingredients[:10]  # 最多返回10个
                    ]
                    return JsonResponse(
                        {
                            "query": query,
                            "match_type": "fuzzy_multiple",
                            "count": ingredients.count(),
                            "ingredients": results,
                            "message": f"找到 {ingredients.count()} 个匹配结果",
                        },
                        status=200,
                    )
            else:
                return JsonResponse({"error": "目标不在数据库中"}, status=404)

    return JsonResponse({"error": "只支持GET请求"}, status=405)


@csrf_exempt
def add_ingredient(request):
    """
    添加新成分
    """
    if request.method == "POST":
        # 从POST请求体中获取数据
        name = request.POST.get("name", "").strip()
        ingredient_type = request.POST.get("type", "").strip()
        label = request.POST.get("label", "").strip()
        desc = request.POST.get("desc", "").strip()

        if not name:
            return JsonResponse({"error": "请提供成分名称"}, status=400)

        # 检查是否已存在同名成分
        if Ingredient.objects.filter(name=name).exists():
            return JsonResponse({"error": "成分已存在"}, status=409)

        try:
            # 创建新成分
            ingredient = Ingredient.objects.create(
                name=name, type=ingredient_type, label=label, desc=desc
            )
            return JsonResponse(
                {
                    "message": "成分添加成功",
                    "ingredient": {
                        "id": ingredient.id,
                        "name": ingredient.name,
                        "type": ingredient.type,
                        "label": ingredient.label,
                        "desc": ingredient.desc,
                    },
                },
                status=201,
            )
        except Exception as e:
            return JsonResponse({"error": f"添加失败: {str(e)}"}, status=500)

    return JsonResponse({"error": "只支持POST请求"}, status=405)


@csrf_exempt
def add_additive(request):
    """
    添加新添加剂
    """
    if request.method == "POST":
        # 从POST请求体中获取数据
        name = request.POST.get("name", "").strip()
        en_name = request.POST.get("en_name", "").strip()
        applicable_range = request.POST.get("applicable_range", "").strip()
        additive_type = request.POST.get("type", "").strip()

        if not name:
            return JsonResponse({"error": "请提供添加剂名称"}, status=400)

        # 检查是否已存在同名添加剂
        if Additive.objects.filter(Q(name=name) | Q(en_name=en_name)).exists():
            return JsonResponse({"error": "添加剂已存在"}, status=409)

        try:
            # 创建新添加剂
            additive = Additive.objects.create(
                name=name, en_name=en_name, applicable_range=applicable_range, type=additive_type
            )
            return JsonResponse(
                {
                    "message": "添加剂添加成功",
                    "additive": {
                        "id": additive.id,
                        "name": additive.name,
                        "en_name": additive.en_name,
                        "applicable_range": additive.applicable_range,
                        "type": additive.type,
                    },
                },
                status=201,
            )
        except Exception as e:
            return JsonResponse({"error": f"添加失败: {str(e)}"}, status=500)

    return JsonResponse({"error": "只支持POST请求"}, status=405)
