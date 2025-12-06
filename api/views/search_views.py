"""
搜索服务 API
负责调用第三方搜索 API（如百度百科），保护 API 密钥
"""

import json
import logging

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from ..services.search_service import search_service
from ..utils import error_response, success_response, validation_error_response

logger = logging.getLogger(__name__)


@swagger_auto_schema(
    method="post",
    operation_description="🔍 搜索成分信息 (POST)\n\n从百度百科搜索添加剂或营养成分的详细信息。\n\n**速率限制**: 30次/小时",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["ingredient"],
        properties={
            "ingredient": openapi.Schema(
                type=openapi.TYPE_STRING, description="要搜索的成分名称"
            ),
        },
        example={"ingredient": "维生素D"},
    ),
    responses={
        200: openapi.Response(
            description="搜索成功",
            examples={
                "application/json": {
                    "ok": True,
                    "data": {
                        "summary": "维生素D是一种脂溶性维生素...",
                        "source": "baidu_baike",
                    },
                }
            },
        ),
        400: "请求参数错误",
        429: "速率限制：超过 30次/小时",
        503: "搜索服务未配置",
    },
    tags=["🔍 搜索服务"],
)
@swagger_auto_schema(
    method="get",
    operation_description="🔍 搜索成分信息 (GET)\n\n从百度百科搜索添加剂或营养成分的详细信息。\n\n**速率限制**: 30次/小时",
    manual_parameters=[
        openapi.Parameter(
            "ingredient",
            openapi.IN_QUERY,
            description="要搜索的成分名称",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={
        200: "搜索成功",
        400: "请求参数错误",
        429: "速率限制：超过 30次/小时",
    },
    tags=["🔍 搜索服务"],
)
@csrf_exempt
@require_http_methods(["POST", "GET"])
@ratelimit(key="ip", rate="30/h", block=True)
def search_ingredient_info(request):
    """
    搜索成分信息（百度百科）

    POST /api/search/ingredient/info
    Body: {"ingredient": "维生素D"}

    或

    GET /api/search/ingredient/info?q=维生素D

    Response:
        {
            "ok": true,
            "title": "维生素D",
            "extract": "维生素D是一种脂溶性维生素..."
        }
    """
    try:
        # 检查 API 配置
        if not search_service.is_configured():
            return error_response(
                message="搜索服务未配置", code="service_not_configured", status=503
            )

        # 获取参数（支持 POST 和 GET）
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                ingredient = (
                    data.get("ingredient") or data.get("q") or data.get("query") or ""
                ).strip()
            except json.JSONDecodeError:
                return error_response(
                    message="无效的 JSON 格式", code="invalid_json", status=400
                )
        else:  # GET
            ingredient = (
                request.GET.get("query")
                or request.GET.get("q")
                or request.GET.get("ingredient")
                or ""
            ).strip()

        # 验证参数
        if not ingredient:
            return validation_error_response(
                {"ingredient": "请提供成分名称（q/query/ingredient）"}
            )

        logger.info(f"搜索成分信息: {ingredient}")

        # 调用服务层
        success, title, extract, error = search_service.search_ingredient(ingredient)

        if not success:
            return error_response(
                message=error or "搜索失败", code="search_failed", status=502
            )

        # 返回成功响应
        return success_response(
            data={
                "title": title,
                "extract": extract,
            },
            message="搜索成功",
        )

    except Exception as e:
        logger.exception(f"搜索成分信息异常: {str(e)}")
        return error_response(
            message="服务器内部错误", code="server_error", detail=str(e), status=500
        )
