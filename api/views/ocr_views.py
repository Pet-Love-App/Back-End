"""
OCR 识别相关 API
使用阿里云高精版OCR进行文字识别
"""

import base64
import logging
import re

from django.views.decorators.csrf import csrf_exempt
from django_ratelimit.decorators import ratelimit
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

from middleware.supabase_auth import require_auth

from ..services.ocr_service import ocr_service
from ..utils import error_response, success_response, validation_error_response

logger = logging.getLogger(__name__)


def extract_image_from_request(request):
    """
    从请求中提取图片数据
    支持两种格式：
    1. multipart/form-data 文件上传
    2. JSON body 中的 base64 图片

    Returns:
        tuple: (image_bytes, content_type, error_message)
    """
    # 方式 1: multipart/form-data 文件上传
    if "image" in request.FILES:
        image_file = request.FILES["image"]
        image_bytes = image_file.read()
        content_type = image_file.content_type or "image/jpeg"
        logger.info(f"OCR 收到文件上传: {image_file.name}, size={len(image_bytes)}")
        return image_bytes, content_type, None

    # 方式 2: JSON body 中的 base64 图片
    if request.data and "image" in request.data:
        image_data = request.data["image"]

        # 检查是否是 base64 数据
        if isinstance(image_data, str):
            # 处理 data URL 格式: data:image/jpeg;base64,xxxxx
            if image_data.startswith("data:"):
                match = re.match(r"data:([^;]+);base64,(.+)", image_data)
                if match:
                    content_type = match.group(1)
                    base64_data = match.group(2)
                    try:
                        image_bytes = base64.b64decode(base64_data)
                        logger.info(
                            f"OCR 收到 base64 图片 (data URL): size={len(image_bytes)}"
                        )
                        return image_bytes, content_type, None
                    except Exception as e:
                        logger.error(f"Base64 解码失败: {e}")
                        return None, None, "Base64 解码失败"

            # 纯 base64 字符串
            else:
                try:
                    image_bytes = base64.b64decode(image_data)
                    logger.info(f"OCR 收到纯 base64 图片: size={len(image_bytes)}")
                    return image_bytes, "image/jpeg", None
                except Exception as e:
                    logger.error(f"Base64 解码失败: {e}")
                    return None, None, "Base64 解码失败"

    return None, None, "请上传图片文件或提供 base64 编码的图片"


@swagger_auto_schema(
    method="post",
    operation_description="""📷 OCR 图片文字识别

识别猫粮配料表图片中的文字内容。

**支持两种上传方式:**
1. `multipart/form-data` - 直接上传图片文件
2. `application/json` - 发送 base64 编码的图片

**需要认证**: Bearer Token
**速率限制**: 20次/小时""",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["image"],
        properties={
            "image": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="图片 base64 编码 (支持 data URL 格式)",
            ),
        },
        example={"image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."},
    ),
    responses={
        200: openapi.Response(
            description="识别成功",
            examples={
                "application/json": {
                    "ok": True,
                    "data": {"text": "鸡肉粉、鱼肉粉、维生素D...", "length": 100},
                }
            },
        ),
        400: "请求参数错误",
        401: "未认证",
        429: "速率限制：超过 20次/小时",
        503: "OCR 服务未配置",
    },
    tags=["📷 OCR 识别服务"],
)
@api_view(["POST"])
@csrf_exempt
@require_auth
@ratelimit(key="user_or_ip", rate="20/h", method="POST", block=True)
def ocr_recognize(request):
    """
    OCR 识别接口（使用阿里云高精版OCR）

    POST /api/ocr/recognize/

    支持两种上传方式:
    1. multipart/form-data: image 字段为图片文件
    2. application/json: image 字段为 base64 编码
    """
    try:
        # 检查配置
        if not ocr_service.is_configured():
            return error_response(
                message="OCR 服务未配置", code="service_not_configured", status=503
            )

        # 提取图片数据
        image_bytes, content_type, error_msg = extract_image_from_request(request)

        if error_msg:
            return validation_error_response({"image": error_msg})

        if not image_bytes:
            return validation_error_response(
                {"image": "请上传图片文件或提供 base64 编码的图片"}
            )

        logger.info(
            f"OCR 识别: content_type={content_type}, size={len(image_bytes)} bytes"
        )

        # 调用服务层
        success, text, error = ocr_service.recognize(image_bytes, content_type)

        if not success:
            return error_response(
                message=error or "OCR 识别失败",
                code="ocr_recognition_failed",
                status=502,
            )

        # 返回成功响应
        return success_response(
            data={"text": text, "length": len(text)}, message="识别成功"
        )

    except Exception as e:
        logger.exception("OCR 识别异常")
        return error_response(
            message="服务器内部错误", code="server_error", detail=str(e), status=500
        )
