"""
OCR 识别相关 API
使用阿里云高精版OCR进行文字识别
"""

import logging

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit

from middleware.supabase_auth import require_auth

from ..services.ocr_service import ocr_service
from ..utils import error_response, success_response, validation_error_response

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
@ratelimit(key="user_or_ip", rate="20/h", method="POST", block=True)
def ocr_recognize(request):
    """
    OCR 识别接口（使用阿里云高精版OCR）

    POST /api/ocr/recognize/
    Body: multipart/form-data
        - image: 图片文件
    """
    try:
        # 检查配置
        if not ocr_service.is_configured():
            return error_response(
                message="OCR 服务未配置", code="service_not_configured", status=503
            )

        # 检查文件
        if "image" not in request.FILES:
            return validation_error_response({"image": "请上传图片文件"})

        image_file = request.FILES["image"]

        # 读取图片数据
        image_bytes = image_file.read()
        content_type = image_file.content_type

        logger.info(f"OCR 识别图片: {image_file.name}, size={len(image_bytes)}")

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
