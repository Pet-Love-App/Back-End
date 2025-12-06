"""
AI 报告相关 API
使用 Supabase 进行数据操作，集成 LLM API
"""

import logging

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

from config.supabase_client import supabase_admin
from middleware.supabase_auth import get_current_user, require_auth

from ..services.ai_service import ai_service
from ..utils import error_response, success_response, validation_error_response

logger = logging.getLogger(__name__)


@swagger_auto_schema(
    method="post",
    operation_description="🤖 LLM 聊天接口 - 分析猫粮成分\n\n使用 AI 模型分析猫粮配料表，识别添加剂、成分并提供营养分析。\n\n**功能特性**：\n- 自动识别添加剂和配料\n- 提取产品标签\n- 安全性和营养分析\n- 动态提取营养成分百分比数据（percent_data 字段根据实际配料表内容动态生成）\n\n**速率限制**: 10次/小时",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["ingredients"],
        properties={
            "ingredients": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="猫粮配料表文本，多个成分用逗号分隔",
            ),
        },
        example={"ingredients": "鸡肉粉, 鱼肉粉, 维生素D, 牛磺酸"},
    ),
    responses={
        200: openapi.Response(
            description="分析成功",
            examples={
                "application/json": {
                    "ok": True,
                    "data": {
                        "additive": ["维生素D", "牛磺酸"],
                        "ingredient": ["鸡肉粉", "鱼肉粉"],
                        "tags": ["高蛋白", "成猫粮"],
                        "safety": "成分安全，无有害添加剂...",
                        "nutrient": "营养分析详述...",
                        "percentage": True,
                        "percent_data": {
                            "crude_protein": 30.0,
                            "crude_fat": 15.0,
                            "carbohydrates": 40.0,
                            "crude_fiber": 5.0,
                            "crude_ash": 5.0,
                            "others": 5.0,
                        },
                    },
                }
            },
        ),
        400: "请求参数错误",
        429: "速率限制：超过 10次/小时",
        503: "AI 服务未配置",
    },
    tags=["🤖 AI 报告服务"],
)
@api_view(["POST"])
@csrf_exempt
@ratelimit(key="ip", rate="10/h", method="POST", block=True)
def llm_chat(request):
    """LLM 聊天接口 - 分析猫粮成分"""
    try:
        # 检查配置
        if not ai_service.is_configured():
            return error_response(
                message="AI 服务未配置", code="service_not_configured", status=503
            )

        # 解析请求体
        import json

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return error_response(
                message="无效的 JSON 格式", code="invalid_json", status=400
            )

        # 获取参数
        ingredients = body.get("ingredients", "").strip()

        # 验证参数
        if not ingredients:
            return validation_error_response({"ingredients": "成分列表不能为空"})

        logger.info(f"LLM 分析成分: {ingredients[:50]}...")

        # 调用服务层
        success, result, error = ai_service.analyze_ingredients(ingredients)

        if not success:
            return error_response(
                message=error or "AI 分析失败", code="ai_analysis_failed", status=502
            )

        # 返回成功响应
        return success_response(data=result, message="分析成功")

    except Exception as e:
        logger.exception("LLM 聊天异常")
        return error_response(
            message="服务器内部错误", code="server_error", detail=str(e), status=500
        )


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def save_report(request):
    """
    保存 AI 报告到 Supabase

    POST /api/ai/save/
    Body: {
        "catfood_id": 1,
        "catfood_name": "某某猫粮",
        "additive": ["维生素D", "维生素A"],
        "ingredient": ["鸡肉粉", "鱼肉"],
        "nutrient": "营养分析内容",
        "health_advice": "健康建议"
    }
    """
    try:
        # 获取当前用户
        user = get_current_user(request)
        if not user:
            return error_response(message="未授权", code="unauthorized", status=401)

        # 解析请求体
        import json

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return error_response(
                message="无效的 JSON 格式", code="invalid_json", status=400
            )

        # 验证必需字段
        catfood_id = body.get("catfood_id")
        if not catfood_id:
            return validation_error_response({"catfood_id": "猫粮 ID 不能为空"})

        # 准备数据
        report_data = {
            "user_id": user.id,
            "catfood_id": catfood_id,
            "catfood_name": body.get("catfood_name", ""),
            "ingredients_text": body.get("ingredients_text", ""),
            "tags": body.get("tags", []),
            "additives": body.get("additive", []),  # 前端可能用 additive 或 additives
            "ingredients": body.get(
                "ingredient", []
            ),  # 前端可能用 ingredient 或 ingredients
            "safety": body.get("safety", ""),
            "nutrient": body.get("nutrient", ""),
            "percentage": body.get("percentage", False),
            "percent_data": body.get("percent_data", {}),
        }

        # 保存到 Supabase
        response = (
            supabase_admin.table("ai_reports")
            .upsert(report_data, on_conflict="user_id,catfood_id")
            .execute()
        )

        if response.data:
            logger.info(f"保存 AI 报告成功: catfood_id={catfood_id}")
            return success_response(
                data=response.data[0] if response.data else None, message="保存成功"
            )
        else:
            logger.error("保存 AI 报告失败")
            return error_response(message="保存失败", code="save_failed", status=500)

    except Exception as e:
        logger.exception("保存 AI 报告异常")
        return error_response(
            message="服务器内部错误", code="server_error", detail=str(e), status=500
        )


@csrf_exempt
@require_http_methods(["GET"])
@require_auth
def get_report(request, catfood_id):
    """
    获取 AI 报告

    GET /api/ai/<catfood_id>/
    """
    try:
        # 获取当前用户
        user = get_current_user(request)
        if not user:
            return error_response(message="未授权", code="unauthorized", status=401)

        # 从 Supabase 查询
        response = (
            supabase_admin.table("ai_reports")
            .select("*")
            .eq("user_id", user.id)
            .eq("catfood_id", catfood_id)
            .execute()
        )

        if response.data:
            logger.info(f"获取 AI 报告成功: catfood_id={catfood_id}")
            return success_response(data=response.data[0], message="获取成功")
        else:
            return error_response(message="报告不存在", code="not_found", status=404)

    except Exception as e:
        logger.exception("获取 AI 报告异常")
        return error_response(
            message="服务器内部错误", code="server_error", detail=str(e), status=500
        )


@csrf_exempt
@require_http_methods(["GET"])
@require_auth
def check_report_exists(request, catfood_id):
    """
    检查 AI 报告是否存在

    GET /api/ai/<catfood_id>/exists/
    """
    try:
        # 获取当前用户
        user = get_current_user(request)
        if not user:
            return error_response(message="未授权", code="unauthorized", status=401)

        # 从 Supabase 查询
        response = (
            supabase_admin.table("ai_reports")
            .select("id")
            .eq("user_id", user.id)
            .eq("catfood_id", catfood_id)
            .execute()
        )

        exists = bool(response.data)

        return success_response(data={"exists": exists}, message="检查完成")

    except Exception as e:
        logger.exception("检查 AI 报告异常")
        return error_response(
            message="服务器内部错误", code="server_error", detail=str(e), status=500
        )


@csrf_exempt
@require_http_methods(["DELETE"])
@require_auth
def delete_report(request, catfood_id):
    """
    删除 AI 报告

    DELETE /api/ai/<catfood_id>/delete/
    """
    try:
        # 获取当前用户
        user = get_current_user(request)
        if not user:
            return error_response(message="未授权", code="unauthorized", status=401)

        # 从 Supabase 删除
        response = (
            supabase_admin.table("ai_reports")
            .delete()
            .eq("user_id", user.id)
            .eq("catfood_id", catfood_id)
            .execute()
        )

        logger.info(f"删除 AI 报告成功: catfood_id={catfood_id}")
        return success_response(message="删除成功")

    except Exception as e:
        logger.exception("删除 AI 报告异常")
        return error_response(
            message="服务器内部错误", code="server_error", detail=str(e), status=500
        )


@csrf_exempt
@require_http_methods(["GET"])
@require_auth
def get_favorite_reports(request):
    """
    获取收藏的 AI 报告列表

    GET /api/ai/favorites/
    """
    try:
        # 获取当前用户
        user = get_current_user(request)
        if not user:
            return error_response(message="未授权", code="unauthorized", status=401)

        # 从 Supabase 查询
        response = (
            supabase_admin.table("favorite_reports")
            .select("*, ai_analysis_reports(*)")
            .eq("user_id", user.id)
            .execute()
        )

        return success_response(data=response.data or [], message="获取成功")

    except Exception as e:
        logger.exception("获取收藏的 AI 报告异常")
        return error_response(
            message="服务器内部错误", code="server_error", detail=str(e), status=500
        )


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def toggle_favorite_report(request):
    """
    切换 AI 报告收藏状态

    POST /api/ai/favorites/toggle/
    Body: {
        "report_id": 123
    }
    """
    try:
        # 获取当前用户
        user = get_current_user(request)
        if not user:
            return error_response(message="未授权", code="unauthorized", status=401)

        # 解析请求体
        import json

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return error_response(
                message="无效的 JSON 格式", code="invalid_json", status=400
            )

        report_id = body.get("report_id")
        if not report_id:
            return validation_error_response({"report_id": "报告 ID 不能为空"})

        # 检查是否已收藏
        check_response = (
            supabase_admin.table("favorite_reports")
            .select("id")
            .eq("user_id", user.id)
            .eq("report_id", report_id)
            .execute()
        )

        if check_response.data:
            # 已收藏，取消收藏
            supabase_admin.table("favorite_reports").delete().eq(
                "id", check_response.data[0]["id"]
            ).execute()
            return success_response(data={"favorited": False}, message="取消收藏成功")
        else:
            # 未收藏，添加收藏
            insert_response = (
                supabase_admin.table("favorite_reports")
                .insert(
                    {
                        "user_id": user.id,
                        "report_id": report_id,
                    }
                )
                .execute()
            )
            return success_response(data={"favorited": True}, message="收藏成功")

    except Exception as e:
        logger.exception("切换 AI 报告收藏状态异常")
        return error_response(
            message="服务器内部错误", code="server_error", detail=str(e), status=500
        )


@csrf_exempt
@require_http_methods(["DELETE"])
@require_auth
def delete_favorite_report(request, favorite_id):
    """
    删除收藏的 AI 报告

    DELETE /api/ai/favorites/<favorite_id>/
    """
    try:
        # 获取当前用户
        user = get_current_user(request)
        if not user:
            return error_response(message="未授权", code="unauthorized", status=401)

        # 从 Supabase 删除
        supabase_admin.table("favorite_reports").delete().eq("id", favorite_id).eq(
            "user_id", user.id
        ).execute()

        return success_response(message="删除成功")

    except Exception as e:
        logger.exception("删除收藏的 AI 报告异常")
        return error_response(
            message="服务器内部错误", code="server_error", detail=str(e), status=500
        )


@csrf_exempt
@require_http_methods(["GET"])
@require_auth
def check_favorite_report(request, report_id):
    """
    检查 AI 报告是否已收藏

    GET /api/ai/favorites/check/<report_id>/
    """
    try:
        # 获取当前用户
        user = get_current_user(request)
        if not user:
            return error_response(message="未授权", code="unauthorized", status=401)

        # 从 Supabase 查询
        response = (
            supabase_admin.table("favorite_reports")
            .select("id")
            .eq("user_id", user.id)
            .eq("report_id", report_id)
            .execute()
        )

        favorited = bool(response.data)

        return success_response(data={"favorited": favorited}, message="检查完成")

    except Exception as e:
        logger.exception("检查 AI 报告收藏状态异常")
        return error_response(
            message="服务器内部错误", code="server_error", detail=str(e), status=500
        )
