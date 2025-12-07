"""
OCR API 测试

测试 OCR 图片识别功能。
"""

from io import BytesIO
from unittest.mock import Mock, patch

from django.test import Client, TestCase
from PIL import Image

from .helpers import FakeUser


class OCRAPITests(TestCase):
    """OCR API 测试"""

    def setUp(self):
        """测试前准备"""
        self.client = Client()

    @patch("middleware.supabase_auth.get_current_user")
    @patch("api.ocr_views.get_ocr_engine")
    def test_ocr_recognize_success(self, mock_ocr, mock_user):
        """测试 OCR 识别成功"""
        # Arrange
        mock_user.return_value = FakeUser()

        mock_ocr_instance = Mock()
        mock_ocr_instance.ocr.return_value = [
            [
                [[[0, 0], [100, 0], [100, 50], [0, 50]], ("鸡肉粉 35%", 0.95)],
                [[[0, 60], [100, 60], [100, 110], [0, 110]], ("鱼肉粉 20%", 0.92)],
            ]
        ]
        mock_ocr.return_value = mock_ocr_instance

        img = Image.new("RGB", (100, 100), color="white")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)
        img_bytes.name = "test.jpg"

        # Act
        response = self.client.post(
            "/api/ocr/recognize/",
            {"image": img_bytes},
            HTTP_AUTHORIZATION="Bearer test-token",
        )

        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("result", data)
        self.assertIn("detected_items", data["result"])

    def test_ocr_recognize_no_image(self):
        """测试 OCR 识别缺少图片"""
        # Act
        response = self.client.post(
            "/api/ocr/recognize/",
            {},
            HTTP_AUTHORIZATION="Bearer test-token",
        )

        # Assert
        self.assertEqual(response.status_code, 400)
