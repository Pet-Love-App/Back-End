import os
import time

import cv2  # 新增：用于图片预处理
import numpy as np
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import OcrResult

# 延迟初始化PaddleOCR（避免启动时加载失败）
ocr = None
ocr_lock = None


def get_ocr_instance(force_new=False):
    """
    获取PaddleOCR实例
    force_new: 是否强制创建新实例（用于错误恢复）
    """
    global ocr

    if force_new or ocr is None:
        try:
            from paddleocr import PaddleOCR

            # 清理旧实例
            if ocr is not None:
                del ocr
                import gc

                gc.collect()

            print("🔄 初始化 PaddleOCR 实例...")

            # 使用最基础的配置（最大兼容性）
            ocr = PaddleOCR(lang="ch", use_angle_cls=False)

            print("✅ PaddleOCR 实例初始化成功")
        except ImportError:
            raise Exception("PaddleOCR未安装，请执行`pip install paddleocr`")
        except Exception as e:
            raise Exception(f"PaddleOCR初始化失败: {str(e)}")
    return ocr


def get_lock():
    """获取线程锁（防止并发问题）"""
    global ocr_lock
    if ocr_lock is None:
        import threading

        ocr_lock = threading.Lock()
    return ocr_lock


# 新增：图片预处理函数（输入本地文件路径，输出处理后的numpy数组）
def preprocess_image(local_path):
    """
    预处理逻辑：压缩尺寸→去噪声→灰度化→增强对比度
    输入：图片本地路径，输出：适配OCR的numpy.ndarray（BGR格式）
    """
    # 1. 读取本地图片（OpenCV默认BGR格式）
    img = cv2.imread(local_path)
    if img is None:
        raise Exception("图片读取失败，请检查文件路径或格式")

    # 2. 按比例压缩（最长边不超过1000px，减少计算量）
    max_size = 1000
    height, width = img.shape[:2]
    if max(height, width) > max_size:
        scale = max_size / max(height, width)
        img = cv2.resize(
            img,
            (int(width * scale), int(height * scale)),
            interpolation=cv2.INTER_AREA,  # 压缩优先保留细节
        )

    # 3. 高斯去噪（去除杂点，避免干扰识别）
    # img = cv2.GaussianBlur(img, (3, 3), 0)

    # 4. 转为灰度图（减少通道数，提速）
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    return gray


def process_image_for_ocr(image_data):
    """
    快速处理图片以适配 OCR 识别
    优化：减少处理步骤，加快速度
    """
    try:
        # 1. 解码图片（支持各种格式）
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise Exception("图片解码失败，不支持的图片格式")

        # 2. 快速调整图片尺寸（优化：降低最大尺寸以加快处理）
        height, width = img.shape[:2]
        max_size = 1280  # 降低最大边长（从1920降到1280）
        min_size = 200  # 提高最小边长

        # 如果图片太小
        if max(height, width) < min_size:
            scale = min_size / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
            print(f"📏 图片放大: {width}x{height} -> {new_width}x{new_height}")

        # 如果图片太大
        elif max(height, width) > max_size:
            scale = max_size / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            print(f"📏 图片缩小: {width}x{height} -> {new_width}x{new_height}")
        else:
            print(f"✅ 图片尺寸合适: {width}x{height}")

        return img

    except Exception as e:
        print(f"❌ 图片处理失败: {str(e)}")
        raise


# OCR 识别接口
@csrf_exempt
def ocr_recognize(request):
    """
    OCR 识别接口
    接收任意格式的图片，后端完成所有预处理，返回识别结果
    """
    if request.method != "POST":
        return JsonResponse({"error": "只支持POST请求"}, status=405)

    if "image" not in request.FILES:
        return JsonResponse({"error": "请上传图片文件"}, status=400)

    image_file = request.FILES["image"]

    try:
        print(f"\n{'=' * 60}")
        print(f"📥 接收图片: {image_file.name}")
        print(f"📦 文件大小: {len(image_file.read()) / 1024:.2f} KB")

        # 重置文件指针
        image_file.seek(0)
        image_data = image_file.read()

        # 1. 处理图片
        print("🔧 开始图片预处理...")
        img = process_image_for_ocr(image_data)

        # 2. 调用 OCR 识别（使用锁防止并发问题）
        print("🔍 开始 OCR 识别...")
        lock = get_lock()

        ocr_output = None
        retry_count = 0
        max_retries = 2

        while retry_count < max_retries and ocr_output is None:
            try:
                with lock:
                    # 如果是重试，创建新的 OCR 实例
                    ocr_instance = get_ocr_instance(force_new=(retry_count > 0))
                    ocr_output = ocr_instance.ocr(img)
            except RuntimeError as e:
                if "std::exception" in str(e) and retry_count < max_retries - 1:
                    print(f"⚠️ OCR 处理失败，尝试重新初始化... (第 {retry_count + 1} 次)")
                    retry_count += 1
                    import time

                    time.sleep(1)  # 等待1秒后重试
                else:
                    raise

        # 3. 解析识别结果
        print("📊 解析识别结果...")
        recognized_texts = []
        confidences = []

        # PaddleOCR 新版本返回 OCRResult 对象
        if ocr_output and len(ocr_output) > 0:
            result = ocr_output[0]

            # 检查是否是字典类型（OCRResult 对象）
            if isinstance(result, dict):
                # 新版 PaddleOCR 返回格式
                recognized_texts = result.get("rec_texts", [])
                confidences = result.get("rec_scores", [])

                print(f"✅ 识别到 {len(recognized_texts)} 行文本")
                for idx, (text, conf) in enumerate(
                    zip(recognized_texts, confidences, strict=False)
                ):
                    print(f"  📝 第 {idx + 1} 行: {text} (置信度: {conf:.4f})")

            # 兼容旧版格式: [[[box], (text, confidence)], ...]
            elif isinstance(result, list):
                for idx, line in enumerate(result):
                    if line and len(line) >= 2:
                        text_info = line[1]
                        if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                            text, confidence = text_info[0], text_info[1]
                            recognized_texts.append(str(text))
                            confidences.append(float(confidence))
                            print(f"  📝 第 {idx + 1} 行: {text} (置信度: {confidence:.4f})")

        # 4. 拼接结果
        if not recognized_texts:
            print("⚠️ 未识别到任何文字")
            return JsonResponse(
                {
                    "message": "未识别到文字",
                    "text": "",
                    "confidence": 0.0,
                },
                status=200,
            )

        full_text = " ".join(recognized_texts)
        avg_confidence = round(sum(confidences) / len(confidences), 4)

        print("✅ 识别成功!")
        print(f"📄 识别文本: {full_text[:100]}{'...' if len(full_text) > 100 else ''}")
        print(f"📊 平均置信度: {avg_confidence}")
        print(f"{'=' * 60}\n")

        # 5. 返回结果
        return JsonResponse(
            {
                "message": "识别成功",
                "text": full_text.strip(),
                "confidence": avg_confidence,
            },
            status=200,
        )

    except ImportError:
        import traceback

        print("❌ OCR 依赖错误：", traceback.format_exc())
        return JsonResponse({"error": "OCR 服务未正确配置，请安装 PaddleOCR"}, status=500)

    except Exception as e:
        import traceback

        error_trace = traceback.format_exc()
        print(f"❌ OCR 处理错误：\n{error_trace}")

        # 提供友好的错误信息
        error_message = str(e)
        if "decode" in error_message.lower():
            error_message = "图片格式错误或已损坏，请重新拍照"
        elif "std::exception" in error_message:
            error_message = "图片处理失败，请尝试拍摄更清晰的照片"
        elif "memory" in error_message.lower():
            error_message = "图片过大，请压缩后重试"

        return JsonResponse({"error": error_message}, status=500)
