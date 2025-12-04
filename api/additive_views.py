"""
添加剂和成分相关 API
使用 Supabase 进行数据操作
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from config.supabase_client import supabase_admin
from middleware.supabase_auth import require_auth
from utils import parse_json_body, require_admin


@csrf_exempt
@require_http_methods(["GET"])
def search_additive(request):
    """
    搜索添加剂（兼容旧项目格式）

    GET /api/additive/search-additive/
    Query params:
        - name 或 q 或 query: 搜索关键词（兼容三种参数名）
        - fuzzy: 是否模糊搜索（默认 true）
        - limit: 返回数量限制（默认20）
    """
    try:
        # 兼容 name、q、query 三种参数名
        query = (
            request.GET.get("name")
            or request.GET.get("query")
            or request.GET.get("q", "")
        )
        query = query.strip()
        limit = int(request.GET.get("limit") or 10)

        if not query:
            return JsonResponse({"error": "请提供搜索关键词"}, status=400)

        # 1. 尝试精确匹配
        exact_result = (
            supabase_admin.table("additives")
            .select("*")
            .eq("name", query)
            .limit(1)
            .execute()
        )

        if exact_result.data:
            additive = exact_result.data[0]
            return JsonResponse(
                {
                    "query": query,
                    "match_type": "exact",
                    "additive": {
                        "id": additive.get("id"),
                        "name": additive.get("name"),
                        "en_name": additive.get("en_name", ""),
                        "applicable_range": additive.get("applicable_range", ""),
                        "type": additive.get("category", additive.get("type", "")),
                        "description": additive.get("description", ""),
                        "safety_level": additive.get("safety_level", ""),
                    },
                },
                status=200,
            )

        # 2. 模糊匹配
        fuzzy_result = (
            supabase_admin.table("additives")
            .select("*")
            .ilike("name", f"%{query}%")
            .limit(limit)
            .execute()
        )

        if fuzzy_result.data:
            # 如果只有一个结果，直接返回
            if len(fuzzy_result.data) == 1:
                additive = fuzzy_result.data[0]
                return JsonResponse(
                    {
                        "query": query,
                        "match_type": "fuzzy_single",
                        "additive": {
                            "id": additive.get("id"),
                            "name": additive.get("name"),
                            "en_name": additive.get("en_name", ""),
                            "applicable_range": additive.get("applicable_range", ""),
                            "type": additive.get("category", additive.get("type", "")),
                            "description": additive.get("description", ""),
                            "safety_level": additive.get("safety_level", ""),
                        },
                    },
                    status=200,
                )
            else:
                # 多个结果：返回列表供用户选择
                results = [
                    {
                        "id": a.get("id"),
                        "name": a.get("name"),
                        "en_name": a.get("en_name", ""),
                        "applicable_range": a.get("applicable_range", ""),
                        "type": a.get("category", a.get("type", "")),
                        "description": a.get("description", ""),
                        "safety_level": a.get("safety_level", ""),
                    }
                    for a in fuzzy_result.data
                ]
                return JsonResponse(
                    {
                        "query": query,
                        "match_type": "fuzzy_multiple",
                        "count": len(fuzzy_result.data),
                        "additives": results,
                        "message": f"找到 {len(fuzzy_result.data)} 个匹配结果",
                    },
                    status=200,
                )
        else:
            return JsonResponse({"error": "目标不在数据库中"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def search_ingredient(request):
    """
    搜索成分（兼容旧项目格式）

    GET /api/additive/search-ingredient/
    Query params:
        - name 或 q 或 query: 搜索关键词（兼容三种参数名）
        - limit: 返回数量限制（默认10）
    """
    try:
        # 兼容 name、q、query 三种参数名
        query = (
            request.GET.get("name")
            or request.GET.get("query")
            or request.GET.get("q", "")
        )
        query = query.strip()
        limit = int(request.GET.get("limit") or 10)

        if not query:
            return JsonResponse({"error": "请提供搜索关键词"}, status=400)

        # 1. 尝试精确匹配
        exact_result = (
            supabase_admin.table("ingredients")
            .select("*")
            .eq("name", query)
            .limit(1)
            .execute()
        )

        if exact_result.data:
            ingredient = exact_result.data[0]
            return JsonResponse(
                {
                    "query": query,
                    "match_type": "exact",
                    "ingredient": {
                        "id": ingredient.get("id"),
                        "name": ingredient.get("name"),
                        "type": ingredient.get("category", ingredient.get("type", "")),
                        "label": ingredient.get("label", ""),
                        "desc": ingredient.get(
                            "description", ingredient.get("desc", "")
                        ),
                        "description": ingredient.get("description", ""),
                        "safety_level": ingredient.get("safety_level", ""),
                    },
                },
                status=200,
            )

        # 2. 模糊匹配
        fuzzy_result = (
            supabase_admin.table("ingredients")
            .select("*")
            .ilike("name", f"%{query}%")
            .limit(limit)
            .execute()
        )

        if fuzzy_result.data:
            # 如果只有一个结果，直接返回
            if len(fuzzy_result.data) == 1:
                ingredient = fuzzy_result.data[0]
                return JsonResponse(
                    {
                        "query": query,
                        "match_type": "fuzzy_single",
                        "ingredient": {
                            "id": ingredient.get("id"),
                            "name": ingredient.get("name"),
                            "type": ingredient.get(
                                "category", ingredient.get("type", "")
                            ),
                            "label": ingredient.get("label", ""),
                            "desc": ingredient.get(
                                "description", ingredient.get("desc", "")
                            ),
                            "description": ingredient.get("description", ""),
                            "safety_level": ingredient.get("safety_level", ""),
                        },
                    },
                    status=200,
                )
            else:
                # 多个结果：返回列表供用户选择
                results = [
                    {
                        "id": i.get("id"),
                        "name": i.get("name"),
                        "type": i.get("category", i.get("type", "")),
                        "label": i.get("label", ""),
                        "desc": i.get("description", i.get("desc", "")),
                        "description": i.get("description", ""),
                        "safety_level": i.get("safety_level", ""),
                    }
                    for i in fuzzy_result.data
                ]
                return JsonResponse(
                    {
                        "query": query,
                        "match_type": "fuzzy_multiple",
                        "count": len(fuzzy_result.data),
                        "ingredients": results,
                        "message": f"找到 {len(fuzzy_result.data)} 个匹配结果",
                    },
                    status=200,
                )
        else:
            return JsonResponse({"error": "目标不在数据库中"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
@require_admin
def add_ingredient(request):
    """
    添加成分（需要管理员权限）

    POST /api/additive/add-ingredient/
    Body: {
        "name": "成分名称",
        "category": "分类",
        "description": "描述",
        "safety_level": "安全等级"
    }
    """
    try:
        try:
            data = parse_json_body(request, default={})
        except ValueError:
            return JsonResponse({"error": "Invalid JSON body"}, status=400)
        name = data.get("name")

        if not name:
            return JsonResponse({"error": "Name is required"}, status=400)

        # 检查是否已存在
        existing = (
            supabase_admin.table("ingredients").select("id").eq("name", name).execute()
        )

        if existing.data:
            return JsonResponse({"error": "Ingredient already exists"}, status=400)

        # 准备数据（ingredients 表没有 alias 字段）
        ingredient_data = {
            "name": name,
            "category": data.get("category", ""),
            "description": data.get("description", ""),
            "safety_level": data.get("safety_level", "unknown"),
        }

        # 插入
        result = supabase_admin.table("ingredients").insert(ingredient_data).execute()

        return JsonResponse(
            {"message": "Ingredient added successfully", "ingredient": result.data[0]},
            status=201,
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
@require_admin
def add_additive(request):
    """
    添加添加剂（需要管理员权限）

    POST /api/additive/add-additive/
    Body: {
        "name": "添加剂名称",
        "category": "分类",
        "description": "描述",
        "safety_level": "安全等级"
    }
    """
    try:
        try:
            data = parse_json_body(request, default={})
        except ValueError:
            return JsonResponse({"error": "Invalid JSON body"}, status=400)
        name = data.get("name")

        if not name:
            return JsonResponse({"error": "Name is required"}, status=400)

        # 检查是否已存在
        existing = (
            supabase_admin.table("additives").select("id").eq("name", name).execute()
        )

        if existing.data:
            return JsonResponse({"error": "Additive already exists"}, status=400)

        # 准备数据（additives 表没有 alias 字段）
        additive_data = {
            "name": name,
            "category": data.get("category", ""),
            "description": data.get("description", ""),
            "safety_level": data.get("safety_level", "unknown"),
        }

        # 插入
        result = supabase_admin.table("additives").insert(additive_data).execute()

        return JsonResponse(
            {"message": "Additive added successfully", "additive": result.data[0]},
            status=201,
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def _fetch_summary(title: str, timeout: int = 20):
    """
    从百度 AppBuilder API 获取成分摘要信息
    返回: (status_code, data)
    """
    import os
    import urllib.parse

    import requests

    # 兼容多种环境变量名
    key = (
        os.getenv("BAIDU_APPBUILDER_KEY")
        or os.getenv("BAIDU_APPBUILDER_API_KEY")
        or os.getenv("BAIDU_API_KEY")
        or ""
    )
    if not key:
        return (0, "BAIDU_APPBUILDER_KEY not configured")

    safe_title = urllib.parse.quote(title.strip())
    url = f"https://appbuilder.baidu.com/v2/baike/lemma/get_content?search_type=lemmaTitle&search_key={safe_title}"

    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        try:
            return resp.status_code, resp.json()
        except Exception:
            return resp.status_code, resp.text
    except Exception as e:
        return 0, str(e)


@csrf_exempt
@require_http_methods(["POST", "GET"])
def get_ingredient_info(request):
    """
    获取成分详细信息（从百度百科）

    POST /api/search/ingredient/info
    Body: {
        "ingredient": "维生素D"
    }
    或
    GET /api/search/ingredient/info?q=维生素D

    返回格式:
    {
        "ok": true,
        "title": "维生素D",
        "extract": "维生素D是一种脂溶性维生素..."
    }
    """
    try:
        # 支持 POST 和 GET 请求
        if request.method == "POST":
            try:
                payload = parse_json_body(request, default={})
            except ValueError:
                return JsonResponse(
                    {
                        "ok": False,
                        "error": {"code": "bad_json", "message": "Invalid JSON"},
                    },
                    status=400,
                    json_dumps_params={"ensure_ascii": False},
                )

            q = (
                payload.get("ingredient")
                or payload.get("q")
                or payload.get("query")
                or ""
            ).strip()
        else:
            # 兼容 q 和 query 两种参数名
            q = request.GET.get("query") or request.GET.get("q", "")
            q = q.strip()

        if not q:
            return JsonResponse(
                {
                    "ok": False,
                    "error": {
                        "code": "missing_ingredient",
                        "message": "Provide 'q' or 'ingredient'",
                    },
                },
                status=400,
                json_dumps_params={"ensure_ascii": False},
            )

        # 调用百度 API 获取摘要
        status, data = _fetch_summary(q)

        if status == 0:
            return JsonResponse(
                {
                    "ok": False,
                    "error": {
                        "code": "network",
                        "message": "request failed",
                        "detail": data,
                    },
                },
                status=502,
                json_dumps_params={"ensure_ascii": False},
            )

        if isinstance(data, dict):
            title = data.get("title") or q
            result = data.get("result") or {}
            extract = result.get("summary", "")

            return JsonResponse(
                {"ok": True, "title": title, "extract": extract},
                status=200,
                json_dumps_params={"ensure_ascii": False},
            )

        return JsonResponse(
            {"ok": False, "error": {"code": "invalid_response", "detail": str(data)}},
            status=502,
            json_dumps_params={"ensure_ascii": False},
        )

    except Exception as e:
        return JsonResponse(
            {"ok": False, "error": {"code": "server_error", "message": str(e)}},
            status=500,
            json_dumps_params={"ensure_ascii": False},
        )
