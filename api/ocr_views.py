"""
OCR 识别相关 API
使用 Google Tesseract OCR 进行文字识别
"""

import os

import cv2
import numpy as np
import pytesseract
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from middleware.supabase_auth import require_auth

# 从环境变量读取 Tesseract 路径（可选）
TESSERACT_CMD = os.getenv("TESSERACT_CMD")
if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def preprocess_image(image_bytes):
    """
    图片预处理：压缩尺寸→灰度化→去噪→二值化
    输入：图片字节数据
    输出：PIL Image 对象（适配 Tesseract）
    """
    # 1. 将字节数据转换为 numpy 数组
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("图片解码失败")

    # 2. 按比例压缩（最长边不超过 2000px，Tesseract 对大图效果更好）
    max_size = 2000
    height, width = img.shape[:2]
    if max(height, width) > max_size:
        scale = max_size / max(height, width)
        img = cv2.resize(
            img, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_AREA
        )

    # 3. 转为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 4. 去噪
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

    # 5. 自适应阈值二值化（Tesseract 对二值图效果更好）
    binary = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # 6. 转换为 PIL Image（pytesseract 接受 PIL Image）
    pil_image = Image.fromarray(binary)

    return pil_image


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def ocr_recognize(request):
    """
    OCR 识别接口

    POST /api/ocr/recognize/
    Body: multipart/form-data
        - image: 图片文件
    """
    try:
        if "image" not in request.FILES:
            return JsonResponse({"error": "Image file is required"}, status=400)

        image_file = request.FILES["image"]

        # 检查文件类型
        allowed_types = ["image/jpeg", "image/png", "image/jpg"]
        if image_file.content_type not in allowed_types:
            return JsonResponse(
                {"error": "Invalid file type. Only JPEG, PNG allowed"}, status=400
            )

        # 检查文件大小 (10MB)
        if image_file.size > 10 * 1024 * 1024:
            return JsonResponse(
                {"error": "File too large. Maximum size is 10MB"}, status=400
            )

        # 读取图片数据
        image_bytes = image_file.read()

        # 图片预处理
        processed_img = preprocess_image(image_bytes)

        # 执行 OCR 识别（使用 Tesseract）
        # 配置参数：
        # --oem 3: 使用默认 OCR 引擎模式（基于 LSTM）
        # --psm 3: 自动页面分割，无方向和脚本检测（默认）
        custom_config = r"--oem 3 --psm 3"

        # 获取详细的识别结果（包含置信度和位置信息）
        data = pytesseract.image_to_data(
            processed_img,
            lang="chi_sim+eng",  # 中英文混合识别
            config=custom_config,
            output_type=pytesseract.Output.DICT,
        )

        # 处理识别结果
        detected_items = []
        n_boxes = len(data["text"])

        for i in range(n_boxes):
            # 过滤掉空文本和置信度为 -1 的结果
            if int(data["conf"][i]) > 0:  # 置信度 > 0 才认为是有效识别
                text = data["text"][i].strip()
                if text:  # 非空文本
                    detected_items.append(
                        {
                            "text": text,
                            "confidence": float(data["conf"][i])
                            / 100.0,  # Tesseract 返回 0-100，转换为 0-1
                        }
                    )

        # 如果没有识别到任何文本，返回空结果
        if not detected_items:
            return JsonResponse({"result": []})

        return JsonResponse({"result": detected_items})

    except pytesseract.TesseractNotFoundError:
        return JsonResponse(
            {
                "error": "Tesseract OCR not found. Please install Tesseract OCR.",
                "detail": "Visit https://github.com/tesseract-ocr/tesseract for installation instructions.",
            },
            status=500,
        )
    except Exception as e:
        return JsonResponse({"error": f"OCR recognition failed: {str(e)}"}, status=500)
