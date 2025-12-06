"""
统一响应格式工具
确保所有 API 返回一致的响应结构
"""

import logging
from typing import Any, Dict, Optional

from django.http import JsonResponse

logger = logging.getLogger(__name__)


def success_response(
    data: Any = None, message: str = "Success", status: int = 200
) -> JsonResponse:
    """
    成功响应

    Args:
        data: 响应数据
        message: 成功消息
        status: HTTP 状态码

    Returns:
        JsonResponse
    """
    response_data = {
        "ok": True,
        "message": message,
    }

    if data is not None:
        response_data["data"] = data

    return JsonResponse(
        response_data, status=status, json_dumps_params={"ensure_ascii": False}
    )


def error_response(
    message: str, code: str = "error", detail: Optional[Any] = None, status: int = 400
) -> JsonResponse:
    """
    错误响应

    Args:
        message: 错误消息
        code: 错误代码
        detail: 详细错误信息
        status: HTTP 状态码

    Returns:
        JsonResponse
    """
    error_data: Dict[str, Any] = {
        "code": code,
        "message": message,
    }

    if detail is not None:
        error_data["detail"] = detail

    logger.warning(f"Error response: {code} - {message}")

    return JsonResponse(
        {"ok": False, "error": error_data},
        status=status,
        json_dumps_params={"ensure_ascii": False},
    )


def validation_error_response(errors: Dict[str, Any]) -> JsonResponse:
    """
    验证错误响应

    Args:
        errors: 字段验证错误字典

    Returns:
        JsonResponse
    """
    return error_response(
        message="Validation failed", code="validation_error", detail=errors, status=400
    )
