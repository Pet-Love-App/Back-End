"""
OCR 识别相关 API
使用阿里云高精版OCR进行文字识别
"""

import base64
import os

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from middleware.supabase_auth import require_auth

# 从环境变量读取阿里云OCR配置
ALIYUN_OCR_APPCODE = os.getenv("ALIYUN_OCR_APPCODE", "4128453694f84dedab4c2f873999cad4")
ALIYUN_OCR_URL = os.getenv(
    "ALIYUN_OCR_URL", "https://gjbsb.market.alicloudapi.com/ocrservice/advanced"
)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def ocr_recognize(request):
    """
    OCR 识别接口（使用阿里云高精版OCR）

    POST /api/ocr/recognize/
    Body: multipart/form-data
        - image: 图片文件
    """
    try:
        if "image" not in request.FILES:
            return JsonResponse({"error": "Image file is required"}, status=400)

        image_file = request.FILES["image"]

        # 检查文件类型
        allowed_types = [
            "image/jpeg",
            "image/png",
            "image/jpg",
            "image/bmp",
            "image/gif",
        ]
        if image_file.content_type not in allowed_types:
            return JsonResponse(
                {"error": "Invalid file type. Only JPEG, PNG, BMP, GIF allowed"},
                status=400,
            )

        # 检查文件大小 (10MB)
        if image_file.size > 10 * 1024 * 1024:
            return JsonResponse(
                {"error": "File too large. Maximum size is 10MB"}, status=400
            )

        # 检查AppCode配置
        if not ALIYUN_OCR_APPCODE:
            return JsonResponse(
                {"error": "ALIYUN_OCR_APPCODE not configured"}, status=500
            )

        # 读取图片数据并转换为base64
        image_bytes = image_file.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        # 准备请求阿里云OCR API
        headers = {
            "Authorization": f"APPCODE {ALIYUN_OCR_APPCODE}",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        }

        # 发送POST请求
        body_data = {"img": image_base64}

        response = requests.post(
            ALIYUN_OCR_URL, headers=headers, data=body_data, timeout=30
        )

        # 检查响应状态
        if response.status_code != 200:
            error_msg = response.text
            return JsonResponse(
                {
                    "error": "OCR API request failed",
                    "detail": error_msg,
                    "status_code": response.status_code,
                },
                status=500,
            )

        # 解析响应结果
        result_data = response.json()

        # 阿里云OCR返回格式示例：
        # {
        #   "content": "识别的完整文本",
        #   "ret": [
        #     {
        #       "word": "单个文字/词语",
        #       "rect": {...},
        #       "prob": {...}
        #     }
        #   ],
        #   "prism_wordsInfo": [...]
        # }

        # 处理返回结果，转换为统一格式
        detected_items = []

        # 优先使用 prism_wordsInfo（更详细）
        if "prism_wordsInfo" in result_data and result_data["prism_wordsInfo"]:
            for item in result_data["prism_wordsInfo"]:
                word = item.get("word", "").strip()
                if word:
                    detected_items.append(
                        {
                            "text": word,
                            "confidence": 0.95,  # 阿里云OCR通常不返回置信度，给一个默认高值
                        }
                    )
        # 备用方案：使用 ret 字段
        elif "ret" in result_data and result_data["ret"]:
            for item in result_data["ret"]:
                word = item.get("word", "").strip()
                if word:
                    detected_items.append({"text": word, "confidence": 0.95})
        # 最后备用：直接使用 content 字段
        elif "content" in result_data and result_data["content"]:
            content = result_data["content"].strip()
            if content:
                # 将整段文本按行或逗号分割
                words = [
                    w.strip()
                    for w in content.replace("\n", ",").split(",")
                    if w.strip()
                ]
                for word in words:
                    detected_items.append({"text": word, "confidence": 0.95})

        # 如果没有识别到任何文本
        if not detected_items:
            return JsonResponse({"result": []})

        return JsonResponse({"result": detected_items})

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": f"OCR API request error: {str(e)}"}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"OCR recognition failed: {str(e)}"}, status=500)
