
import os
import time
import numpy as np
import cv2  # 新增：用于图片预处理
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import OcrResult

# 延迟初始化PaddleOCR（避免启动时加载失败）
ocr = None

def get_ocr_instance():
    """获取PaddleOCR实例（单例模式）"""
    global ocr
    if ocr is None:
        try:
            from paddleocr import PaddleOCR
            ocr = PaddleOCR(lang='ch',use_angle_cls=False)  # 关闭方向分类提速
        except ImportError:
            raise Exception("PaddleOCR未安装，请执行`pip install paddleocr`")
        except Exception as e:
            raise Exception(f"PaddleOCR初始化失败: {str(e)}")
    return ocr

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
            interpolation=cv2.INTER_AREA  # 压缩优先保留细节
        )
    
    # 3. 高斯去噪（去除杂点，避免干扰识别）
    # img = cv2.GaussianBlur(img, (3, 3), 0)
    
    # 4. 转为灰度图（减少通道数，提速）
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    return gray

# 在原views.py中修改ocr_recognize函数
@csrf_exempt
def ocr_recognize(request):
    """临时调整：不保存数据库、不做预处理、直接回传结果"""
    if request.method != "POST":
        return JsonResponse({"error": "只支持POST请求"}, status=405)

    if "image" not in request.FILES:
        return JsonResponse({"error": "请上传图片文件"}, status=400)
    image_file = request.FILES["image"]

    try:
        # 1. 直接读取图片二进制数据（不保存到磁盘）
        image_data = image_file.read()
        
        # 2. 跳过预处理（模拟前端已处理或无需处理）
        # 注意：若PaddleOCR必须传入numpy数组，需临时转换
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise Exception("图片解码失败")
        
        # 3. 调用OCR识别
        ocr_instance = get_ocr_instance()
        ocr_output = ocr_instance.ocr(img)  # 传入解码后的图片
        
        # 4. 处理识别结果
        recognized_texts = []
        confidences = []
        if ocr_output and isinstance(ocr_output[0], dict):
            ocr_dict = ocr_output[0]
            recognized_texts = ocr_dict.get('rec_texts', [])
            confidences = ocr_dict.get('rec_scores', [])
        
        full_text = ' '.join(recognized_texts)
        avg_confidence = round(sum(confidences) / len(confidences), 4) if confidences else 0.0
        
        # 5. 不保存数据库，直接返回结果（关键修改）
        return JsonResponse({
            "message": "识别成功（未保存数据库）",
            "text": full_text.strip(),
            "confidence": avg_confidence,
                
            
        }, status=200)  # 用200表示成功（非创建资源）

    except Exception as e:
        import traceback
        print("OCR处理错误详情：", traceback.format_exc())
        return JsonResponse({"error": f"处理失败: {str(e)}"}, status=500)


# @csrf_exempt
# def ocr_recognize(request):
    """优化后的OCR识别接口（适配PaddleOCR 3.3.1）"""
    if request.method != "POST":
        return JsonResponse({"error": "只支持POST请求"}, status=405)

    # 校验文件
    if "image" not in request.FILES:
        return JsonResponse({"error": "请上传图片文件"}, status=400)
    image_file = request.FILES["image"]

    try:
        # 保存图片（使用Django文件存储机制）
        timestamp = int(time.time())
        filename = f"{timestamp}_{image_file.name}"
        file_path = default_storage.save(f"ocr_images/{filename}", ContentFile(image_file.read()))
        local_path = default_storage.path(file_path)  # 获取本地路径用于OCR识别
        
        # 新增：调用预处理函数（仅添加这一行，不改动原有保存逻辑）
        processed_img = preprocess_image(local_path)
        
        # 调用OCR识别：传入预处理后的numpy数组（替代原本地路径）
        ocr_instance = get_ocr_instance()
        ocr_output = ocr_instance.ocr(processed_img)  # 3.3.1支持ndarray输入
        
        # 处理识别结果（适配3.x版本的列表格式）
        recognized_texts = []  # 存储所有识别文本
        confidences = []       # 存储所有置信度
        
        # 遍历OCR结果（支持多页，此处取第1页）
        if ocr_output and isinstance(ocr_output[0], dict):
            ocr_dict = ocr_output[0]  # 提取列表中的字典
            # 2. 从字典中获取rec_texts（识别文本列表）和rec_scores（置信度列表）
            recognized_texts = ocr_dict.get('rec_texts', [])
            confidences = ocr_dict.get('rec_scores', [])
        
        # 拼接文本和计算平均置信度
        full_text = ' '.join(recognized_texts)
        avg_confidence = round(sum(confidences) / len(confidences), 4) if confidences else 0.0
        # print("完整识别文本：", full_text)
        # print("平均置信度：", avg_confidence)
        # 保存到数据库
        ocr_result = OcrResult.objects.create(
            image=file_path,
            recognized_text=full_text.strip(),
            confidence=avg_confidence
        )

        return JsonResponse({
            "message": "识别成功",
            "result": {
                "id": ocr_result.id,
                "text": ocr_result.recognized_text,
                "confidence": ocr_result.confidence,
                "image_url": ocr_result.image_url,  # 确保模型中定义了image_url属性
                "created_at": ocr_result.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        }, status=201)

    except Exception as e:
        import traceback
        print("OCR处理错误详情：", traceback.format_exc())
        if isinstance(e, ImportError):
            return JsonResponse({"error": "依赖缺失: 请安装PaddleOCR"}, status=500)
        elif "PaddleOCR初始化失败" in str(e):
            return JsonResponse({"error": f"服务初始化失败: {str(e)}"}, status=500)
        else:
            return JsonResponse({"error": f"处理失败: {str(e)}"}, status=500)