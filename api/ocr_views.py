"""
OCR 识别相关 API
使用 PaddleOCR 进行文字识别
"""

import cv2
import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from paddleocr import PaddleOCR

from middleware.supabase_auth import require_auth

# 初始化 PaddleOCR（全局单例，避免重复加载模型）
ocr_engine = None


def get_ocr_engine():
    """获取 OCR 引擎实例（懒加载）"""
    global ocr_engine
    if ocr_engine is None:
        ocr_engine = PaddleOCR(
            lang="ch",  # 中文识别
            use_angle_cls=False,  # 关闭方向分类，提速
            show_log=False,  # 关闭日志输出
        )
    return ocr_engine


def preprocess_image(image_bytes):
    """
    图片预处理：压缩尺寸→灰度化→增强对比度
    输入：图片字节数据
    输出：适配 OCR 的 numpy.ndarray（BGR 格式）
    """
    # 1. 将字节数据转换为 numpy 数组
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("图片解码失败")

    # 2. 按比例压缩（最长边不超过 1000px）
    max_size = 1000
    height, width = img.shape[:2]
    if max(height, width) > max_size:
        scale = max_size / max(height, width)
        img = cv2.resize(
            img, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_AREA
        )

    # 3. 转为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 4. 自适应阈值增强（突出文本）
    threshold = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )

    # 5. 转回 BGR 格式（PaddleOCR 要求）
    return cv2.cvtColor(threshold, cv2.COLOR_GRAY2BGR)


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
            return JsonResponse({"error": "Invalid file type. Only JPEG, PNG allowed"}, status=400)

        # 检查文件大小 (10MB)
        if image_file.size > 10 * 1024 * 1024:
            return JsonResponse({"error": "File too large. Maximum size is 10MB"}, status=400)

        # 读取图片数据
        image_bytes = image_file.read()

        # 图片预处理
        processed_img = preprocess_image(image_bytes)

        # 执行 OCR 识别
        ocr = get_ocr_engine()
        result = ocr.ocr(processed_img)

        # 处理识别结果
        if not result or not result[0]:
            return JsonResponse(
                {
                    "result": {
                        "text": "",
                        "confidence": 0.0,
                        "detected_items": [],
                    }
                }
            )

        # 提取文本和置信度
        detected_items = []
        all_texts = []

        for line in result[0]:
            if isinstance(line, (list, tuple)) and len(line) >= 2:
                text = line[1][0] if isinstance(line[1], (list, tuple)) else str(line[1])
                confidence = (
                    line[1][1] if isinstance(line[1], (list, tuple)) and len(line[1]) > 1 else 1.0
                )

                detected_items.append({"text": text, "confidence": float(confidence)})
                all_texts.append(text)

        # 计算平均置信度
        avg_confidence = (
            sum(item["confidence"] for item in detected_items) / len(detected_items)
            if detected_items
            else 0.0
        )

        return JsonResponse(
            {
                "result": {
                    "text": "\n".join(all_texts),
                    "confidence": avg_confidence,
                    "detected_items": detected_items,
                }
            }
        )

    except Exception as e:
        return JsonResponse({"error": f"OCR recognition failed: {str(e)}"}, status=500)
