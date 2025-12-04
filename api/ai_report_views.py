"""
AI 报告相关 API
使用 Supabase 进行数据操作，集成 OpenAI API
"""

import json
import os

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from config.supabase_client import supabase_admin
from middleware.supabase_auth import get_current_user, require_auth
from utils import parse_json_body, safe_single

# OpenAI API 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")


def _post_json(url, headers, data):
    """
    发送 POST 请求到 OpenAI API
    返回: (status_code, response_text)
    """
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        return (response.status_code, response.text)
    except requests.exceptions.RequestException as e:
        return (0, str(e))


@csrf_exempt
@require_http_methods(["POST"])
def llm_chat(request):
    """
    LLM 聊天接口 - 分析猫粮成分

    POST /api/ai/llm/chat
    Body: {
        "ingredients": "鸡肉粉, 鱼肉粉, 维生素D"
    }

    返回格式:
    {
        "additive": ["维生素D"],
        "ingredient": ["鸡肉粉", "鱼肉粉"],
        "nutrient": "营养分析详述",
        "safety": "安全评估",
        "percentage": true/false,
        "percent_data": {
            "crude_protein": 30.0,
            "crude_fat": 10.0,
            "carbohydrates": 40.0,
            "crude_fiber": 5.0,
            "crude_ash": 5.0,
            "others": 10.0
        }
    }
    """
    try:
        try:
            data = parse_json_body(request)
        except ValueError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        ingredients = data.get("ingredients")

        if not ingredients:
            return JsonResponse({"error": "ingredients field is required"}, status=400)

        # 检查 API Key
        if not OPENAI_API_KEY:
            return JsonResponse(
                {
                    "ok": False,
                    "error": {
                        "message": "OPENAI_API_KEY not configured",
                        "type": "configuration_error",
                    },
                },
                status=502,
            )

        # 构建 prompt
        prompt = f"""请分析以下猫粮成分表，并以 JSON 格式返回分析结果：

成分：{ingredients}

请返回以下格式的 JSON（不要包含任何其他文本）：
{{
    "tags": ["标签1", "标签2"],
    "additives": ["添加剂1", "添加剂2"],
    "identified_nutrients": ["营养素1", "营养素2"],
    "safety": "安全评估（安全/需注意/不安全）",
    "nutrient": "详细的营养分析说明",
    "percentage": true,
    "crude_protein": 30.0,
    "crude_fat": 10.0,
    "carbohydrates": 40.0,
    "crude_fiber": 5.0,
    "crude_ash": 5.0
}}

注意：
1. percentage 为 true 时，各成分百分比总和应为 100
2. 如果无法确定某个值，设置为 null
3. safety 只能是：安全、需注意、不安全 之一
"""

        # 调用 OpenAI API
        url = f"{OPENAI_API_BASE}/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }

        request_data = {
            "model": OPENAI_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1000,
        }

        status_code, response_text = _post_json(url, headers, request_data)

        # 处理网络错误
        if status_code == 0:
            return JsonResponse(
                {
                    "ok": False,
                    "error": {"message": response_text, "type": "network_error"},
                },
                status=502,
            )

        # 处理 API 错误
        if status_code != 200:
            return JsonResponse(
                {
                    "ok": False,
                    "error": {
                        "message": f"OpenAI API error: {response_text}",
                        "type": "api_error",
                    },
                },
                status=502,
            )

        # 解析响应
        try:
            response_json = json.loads(response_text)
            content = response_json["choices"][0]["message"]["content"]

            # 尝试解析 AI 返回的 JSON
            try:
                ai_result = json.loads(content)
            except json.JSONDecodeError:
                # 如果 AI 返回的不是有效 JSON，返回默认结构
                ai_result = {}

            # 构建标准响应格式
            result = {
                "additive": ai_result.get("additives", []),
                "ingredient": ai_result.get("identified_nutrients", []),
                "nutrient": ai_result.get("nutrient", ""),
                "safety": ai_result.get("safety", ""),
                "percentage": ai_result.get("percentage", False),
                "percent_data": {
                    "crude_protein": ai_result.get("crude_protein"),
                    "crude_fat": ai_result.get("crude_fat"),
                    "carbohydrates": ai_result.get("carbohydrates"),
                    "crude_fiber": ai_result.get("crude_fiber"),
                    "crude_ash": ai_result.get("crude_ash"),
                    "others": None,
                },
            }

            # 如果有百分比数据，计算 others
            if result["percentage"]:
                total = sum(
                    v or 0
                    for v in [
                        result["percent_data"]["crude_protein"],
                        result["percent_data"]["crude_fat"],
                        result["percent_data"]["carbohydrates"],
                        result["percent_data"]["crude_fiber"],
                        result["percent_data"]["crude_ash"],
                    ]
                )
                result["percent_data"]["others"] = max(0, 100 - total)

            return JsonResponse(result)

        except (KeyError, json.JSONDecodeError):
            # 解析失败，返回默认结构
            return JsonResponse(
                {
                    "additive": [],
                    "ingredient": [],
                    "nutrient": "",
                    "safety": "",
                    "percentage": False,
                    "percent_data": {
                        "crude_protein": None,
                        "crude_fat": None,
                        "carbohydrates": None,
                        "crude_fiber": None,
                        "crude_ash": None,
                        "others": None,
                    },
                }
            )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def save_report(request):
    """
    保存或更新 AI 分析报告

    POST /api/ai/save/
    Body: {
        "catfood_id": 123,
        "content": "报告内容",
        "analysis_data": {...}
    }
    """
    try:
        user = get_current_user(request)
        try:
            data = parse_json_body(request)
        except ValueError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        catfood_id = data.get("catfood_id")
        content = data.get("content")

        if not catfood_id or not content:
            return JsonResponse(
                {"error": "catfood_id and content are required"}, status=400
            )

        # 检查是否已存在报告（每个猫粮只有一条报告）
        existing = (
            supabase_admin.table("ai_analysis_reports")
            .select("id")
            .eq("catfood_id", catfood_id)
            .execute()
        )

        # 构建报告数据（不包含 user_id，因为报告是公共的）
        report_data = {
            "catfood_id": catfood_id,
            "ingredients_text": content,
            "safety": data.get("safety"),
            "nutrient": data.get("nutrient"),
            "percentage": data.get("percentage", False),
            "percent_data": data.get("percent_data", {}),
            "tags": data.get("tags", []),
            "additives": data.get("additives", []),
            "ingredients": data.get("ingredients", []),
        }

        if existing.data:
            # 更新现有报告
            result = (
                supabase_admin.table("ai_analysis_reports")
                .update(report_data)
                .eq("id", existing.data[0]["id"])
                .execute()
            )
            message = "Report updated successfully"
        else:
            # 创建新报告
            result = (
                supabase_admin.table("ai_analysis_reports")
                .insert(report_data)
                .execute()
            )
            message = "Report saved successfully"

        return JsonResponse({"message": message, "report": result.data[0]}, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@require_auth
def get_report(request, catfood_id):
    """
    获取猫粮的 AI 分析报告

    GET /api/ai/<catfood_id>/
    """
    try:
        user = get_current_user(request)

        # 查询报告（报告是公共的，不需要检查 user_id）
        report_result = (
            supabase_admin.table("ai_analysis_reports")
            .select("*, catfood:catfoods(*)")
            .eq("catfood_id", catfood_id)
            .execute()
        )
        report_data, error = safe_single(report_result, "Report not found")
        if error:
            return JsonResponse({"error": error}, status=404)

        return JsonResponse({"report": report_data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@require_auth
def check_report_exists(request, catfood_id):
    """
    检查报告是否存在

    GET /api/ai/<catfood_id>/exists/
    """
    try:
        user = get_current_user(request)

        # 检查是否存在（报告是公共的）
        report = (
            supabase_admin.table("ai_analysis_reports")
            .select("id")
            .eq("catfood_id", catfood_id)
            .execute()
        )

        exists = len(report.data) > 0

        return JsonResponse({"exists": exists})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@require_auth
def delete_report(request, catfood_id):
    """
    删除报告（用于重新生成）

    DELETE /api/ai/<catfood_id>/delete/
    """
    try:
        user = get_current_user(request)

        # 查找报告（报告是公共的）
        report_result = (
            supabase_admin.table("ai_analysis_reports")
            .select("id")
            .eq("catfood_id", catfood_id)
            .execute()
        )
        report_data, error = safe_single(report_result, "Report not found")
        if error:
            return JsonResponse({"error": error}, status=404)

        # 删除报告
        supabase_admin.table("ai_analysis_reports").delete().eq(
            "id", report_data["id"]
        ).execute()

        return JsonResponse({"message": "Report deleted successfully"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@require_auth
def get_favorite_reports(request):
    """
    获取收藏的报告列表

    GET /api/ai/favorites/
    """
    try:
        user = get_current_user(request)

        # 查询收藏，并关联报告和猫粮信息
        result = (
            supabase_admin.table("favorite_reports")
            .select("*, report:ai_analysis_reports(*, catfood:catfoods(*))")
            .eq("user_id", user.id)
            .order("created_at", desc=True)
            .execute()
        )

        return JsonResponse({"favorites": result.data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def toggle_favorite_report(request):
    """
    切换报告收藏状态

    POST /api/ai/favorites/toggle/
    Body: {
        "report_id": 123
    }
    """
    try:
        user = get_current_user(request)
        try:
            data = parse_json_body(request)
        except ValueError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        report_id = data.get("report_id")
        if not report_id:
            return JsonResponse({"error": "report_id is required"}, status=400)

        # 检查是否已收藏
        existing = (
            supabase_admin.table("favorite_reports")
            .select("id")
            .eq("report_id", report_id)
            .eq("user_id", user.id)
            .execute()
        )

        if existing.data:
            # 取消收藏
            supabase_admin.table("favorite_reports").delete().eq(
                "id", existing.data[0]["id"]
            ).execute()
            return JsonResponse(
                {"message": "Unfavorited successfully", "favorited": False}
            )
        else:
            # 添加收藏
            favorite_data = {
                "report_id": report_id,
                "user_id": user.id,
            }
            supabase_admin.table("favorite_reports").insert(favorite_data).execute()
            return JsonResponse(
                {"message": "Favorited successfully", "favorited": True}
            )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@require_auth
def delete_favorite_report(request, favorite_id):
    """
    删除收藏

    DELETE /api/ai/favorites/<favorite_id>/
    """
    try:
        user = get_current_user(request)

        # 验证收藏所有权
        favorite_result = (
            supabase_admin.table("favorite_reports")
            .select("*")
            .eq("id", favorite_id)
            .eq("user_id", user.id)
            .execute()
        )
        favorite_data, error = safe_single(favorite_result, "Favorite not found")
        if error:
            return JsonResponse({"error": error}, status=404)

        # 删除收藏
        supabase_admin.table("favorite_reports").delete().eq(
            "id", favorite_data["id"]
        ).execute()

        return JsonResponse({"message": "Favorite deleted successfully"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@require_auth
def check_favorite_report(request, report_id):
    """
    检查是否已收藏

    GET /api/ai/favorites/check/<report_id>/
    """
    try:
        user = get_current_user(request)

        # 检查是否已收藏
        favorite = (
            supabase_admin.table("favorite_reports")
            .select("id")
            .eq("report_id", report_id)
            .eq("user_id", user.id)
            .execute()
        )

        favorited = len(favorite.data) > 0

        return JsonResponse({"favorited": favorited})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
