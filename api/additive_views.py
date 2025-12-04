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
    搜索添加剂

    GET /api/additive/search-additive/
    Query params:
        - q 或 query: 搜索关键词（兼容两种参数名）
        - limit: 返回数量限制（默认20）
    """
    try:
        # 兼容 q 和 query 两种参数名
        query = request.GET.get("query") or request.GET.get("q", "")
        query = query.strip()
        limit = int(request.GET.get("limit") or 20)

        if not query:
            return JsonResponse({"error": "Search query is required"}, status=400)

        # 搜索添加剂（按名称）
        result = (
            supabase_admin.table("additives")
            .select("*")
            .ilike("name", f"%{query}%")
            .limit(limit)
            .execute()
        )

        return JsonResponse({"additives": result.data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def search_ingredient(request):
    """
    搜索成分

    GET /api/additive/search-ingredient/
    Query params:
        - q 或 query: 搜索关键词（兼容两种参数名）
        - limit: 返回数量限制（默认20）
    """
    try:
        # 兼容 q 和 query 两种参数名
        query = request.GET.get("query") or request.GET.get("q", "")
        query = query.strip()
        limit = int(request.GET.get("limit") or 20)

        if not query:
            return JsonResponse({"error": "Search query is required"}, status=400)

        # 搜索成分（按名称）
        result = (
            supabase_admin.table("ingredients")
            .select("*")
            .ilike("name", f"%{query}%")
            .limit(limit)
            .execute()
        )

        return JsonResponse({"ingredients": result.data})

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

    key = os.getenv("BAIDU_APPBUILDER_KEY", "")
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
