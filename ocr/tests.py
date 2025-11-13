# from django.test import TestCase, Client
# from django.urls import reverse
# from django.core.files.uploadedfile import SimpleUploadedFile
# from .models import OcrResult
# import os

# class OcrRecognizeTests(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.url = reverse("ocr_recognize")
#         # 准备测试图片（可替换为实际测试图片路径）
#         self.test_image = SimpleUploadedFile(
#             "test.jpg",
#             b"file_content",  # 实际测试时可替换为真实图片二进制数据
#             content_type="image/jpeg"
#         )

#     def test_valid_image_upload(self):
#         """测试正常上传图片（需PaddleOCR环境支持）"""
#         # 读取真实测试图片（替换为你的图片路径）
#         image_path = os.path.join(os.path.dirname(__file__), "tests/image2.png")
#         with open(image_path, "rb") as f:
#             test_image = SimpleUploadedFile(
#                 "image.jpg",
#                 f.read(),
#                 content_type="image/png"
#             )
        
#         response = self.client.post(self.url, {"image": test_image})
#         print(response.json())
#         self.assertEqual(response.status_code, 201)  # 现在应返回201
#         # 其他断言...

#     def test_support_only_post(self):
#         """测试只支持POST请求"""
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 405)
#         self.assertEqual(response.json()["error"], "只支持POST请求")

#     def test_no_image_provided(self):
#         """测试未上传图片的情况"""
#         response = self.client.post(self.url, {})
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.json()["error"], "请上传图片文件")

#     # def test_valid_image_upload(self):
#     #     """测试正常上传图片（需PaddleOCR环境支持）"""
#     #     # 注意：实际运行需确保PaddleOCR已安装且模型可加载
#     #     response = self.client.post(self.url, {"image": self.test_image})
#     #     self.assertEqual(response.status_code, 201)
#     #     self.assertIn("result", response.json())
#     #     # 验证数据库记录
#     #     self.assertEqual(OcrResult.objects.count(), 1)
#     #     ocr_result = OcrResult.objects.first()
#     #     self.assertIsNotNone(ocr_result.image)

#     # def test_invalid_file_type(self):
#     #     """测试上传非图片文件"""
#     #     invalid_file = SimpleUploadedFile(
#     #         "test.txt",
#     #         b"this is a text file",
#     #         content_type="text/plain"
#     #     )
#     #     response = self.client.post(self.url, {"image": invalid_file})
#     #     # 非图片可能被PaddleOCR识别失败，返回500
#     #     self.assertEqual(response.status_code, 500)
#     #     self.assertIn("error", response.json())

#     def tearDown(self):
#         """清理测试生成的文件"""
#         for result in OcrResult.objects.all():
#             if result.image:
#                 if os.path.exists(result.image.path):
#                     os.remove(result.image.path)
#         OcrResult.objects.all().delete()

from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import OcrResult
from .views import preprocess_image  # 复用视图中的预处理函数（若已包含灰度化）
import os
import cv2
import numpy as np

class OcrRecognizeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("ocr_recognize")
        self.image_path = os.path.join(os.path.dirname(__file__), "tests/image2.png")
        # 确保测试图片存在
        if not os.path.exists(self.image_path):
            raise FileNotFoundError(f"测试图片不存在: {self.image_path}")

    def _preprocess_test_image(self, image_path):
        """前端风格预处理：读取原图→转为灰度图→压缩→返回可上传文件"""
        # 1. 读取原始图片（使用OpenCV直接处理，模拟前端逻辑）
        img = cv2.imread(image_path)
        if img is None:
            raise Exception(f"无法读取图片: {image_path}")
        
        # 2. 转为灰度图（核心预处理步骤）
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 3. 按比例压缩（可选，模拟前端减少传输量）
        max_size = 1000  # 与前端保持一致的压缩尺寸
        height, width = gray_img.shape[:2]
        if max(height, width) > max_size:
            scale = max_size / max(height, width)
            gray_img = cv2.resize(
                gray_img,
                (int(width * scale), int(height * scale)),
                interpolation=cv2.INTER_AREA
            )
        
        # 4. 转换为可上传的PNG文件（保持灰度图的单通道特性）
        # 注意：OpenCV imencode会将单通道灰度图编码为3通道，需特殊处理
        _, buffer = cv2.imencode('.png', gray_img)
        return SimpleUploadedFile(
            "grayscale_test.png",
            buffer.tobytes(),
            content_type="image/png"
        )

    def test_valid_image_upload_with_gray_preprocessing(self):
        """测试前端预处理（灰度化）后的图片上传"""
        # 生成灰度图并上传
        gray_test_image = self._preprocess_test_image(self.image_path)
        response = self.client.post(self.url, {"image": gray_test_image})
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        print(response_data["text"])
        

    def test_support_only_post(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()["error"], "只支持POST请求")

    def test_no_image_provided(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "请上传图片文件")

    def tearDown(self):
        """清理测试数据"""
        OcrResult.objects.all().delete()