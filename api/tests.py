"""
API 单元测试
测试 Supabase 集成的 API 端点
"""

import json
from unittest.mock import Mock, patch

from django.test import Client, TestCase


class AuthAPITests(TestCase):
    """认证 API 测试"""

    def setUp(self):
        self.client = Client()

    @patch("api.auth_views.supabase")
    @patch("api.auth_views.supabase_admin")
    def test_register_success(self, mock_admin, mock_supabase):
        """测试用户注册成功"""
        # Mock Supabase 响应
        mock_user = Mock()
        mock_user.id = "test-uuid"
        mock_user.email = "test@example.com"

        mock_session = Mock()
        mock_session.access_token = "test-access-token"
        mock_session.refresh_token = "test-refresh-token"

        mock_auth_response = Mock()
        mock_auth_response.user = mock_user
        mock_auth_response.session = mock_session

        mock_supabase.auth.sign_up.return_value = mock_auth_response

        # Mock profile 和 reputation 创建
        mock_admin.table().insert().execute.return_value = Mock(data=[{"id": "test-uuid"}])
        mock_admin.table().select().eq().execute.return_value = Mock(data=[])

        # 发送请求
        response = self.client.post(
            "/api/auth/register/",
            data=json.dumps(
                {"email": "test@example.com", "password": "password123", "username": "testuser"}
            ),
            content_type="application/json",
        )

        # 验证响应
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["message"], "Registration successful")
        self.assertEqual(data["user"]["email"], "test@example.com")

    def test_register_missing_fields(self):
        """测试注册缺少必填字段"""
        response = self.client.post(
            "/api/auth/register/",
            data=json.dumps({"email": "test@example.com"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)


class CatfoodAPITests(TestCase):
    """猫粮 API 测试"""

    def setUp(self):
        self.client = Client()

    @patch("api.catfood_views.supabase_admin")
    def test_list_catfoods(self, mock_admin):
        """测试获取猫粮列表"""
        # Mock Supabase 响应
        mock_result = Mock()
        mock_result.data = [
            {"id": 1, "name": "皇家猫粮", "brand": "Royal Canin"},
            {"id": 2, "name": "渴望猫粮", "brand": "Orijen"},
        ]
        mock_result.count = 2

        mock_admin.table().select().order().range().execute.return_value = mock_result
        mock_admin.table().select().execute.return_value = mock_result

        # 发送请求
        response = self.client.get("/api/catfoods/")

        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("catfoods", data)
        self.assertEqual(len(data["catfoods"]), 2)


class OCRAPITests(TestCase):
    """OCR API 测试"""

    def setUp(self):
        self.client = Client()

    @patch("api.ocr_views.get_current_user")
    @patch("api.ocr_views.get_ocr_engine")
    @patch("api.ocr_views.preprocess_image")
    def test_ocr_recognize_success(self, mock_preprocess, mock_ocr, mock_user):
        """测试 OCR 识别成功"""
        # Mock 用户认证
        mock_user.return_value = Mock(id="test-uuid")

        # Mock OCR 引擎
        mock_ocr_instance = Mock()
        mock_ocr_instance.ocr.return_value = [
            [
                [[[0, 0], [100, 0], [100, 50], [0, 50]], ("鸡肉粉 35%", 0.95)],
                [[[0, 60], [100, 60], [100, 110], [0, 110]], ("鱼肉粉 20%", 0.92)],
            ]
        ]
        mock_ocr.return_value = mock_ocr_instance

        # Mock 图片预处理
        mock_preprocess.return_value = Mock()

        # 创建测试图片
        from io.BytesIO import BytesIO

        from PIL import Image

        img = Image.new("RGB", (100, 100), color="white")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        # 发送请求
        response = self.client.post(
            "/api/ocr/recognize/",
            {"image": img_bytes},
            HTTP_AUTHORIZATION="Bearer test-token",
        )

        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("result", data)
        self.assertIn("detected_items", data["result"])


class AIReportAPITests(TestCase):
    """AI 报告 API 测试"""

    def setUp(self):
        self.client = Client()

    @patch("api.ai_report_views._post_json")
    def test_llm_chat_success(self, mock_post):
        """测试 LLM 聊天成功"""
        # Mock OpenAI API 响应
        ai_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "tags": ["成猫粮", "高蛋白"],
                                "additives": ["维生素D"],
                                "identified_nutrients": ["鸡肉粉", "鱼肉粉"],
                                "safety": "安全",
                                "nutrient": "营养均衡",
                                "percentage": True,
                                "crude_protein": 30.0,
                                "crude_fat": 10.0,
                                "carbohydrates": 40.0,
                                "crude_fiber": 5.0,
                                "crude_ash": 5.0,
                            }
                        )
                    }
                }
            ]
        }

        mock_post.return_value = (200, json.dumps(ai_response))

        # 发送请求
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            response = self.client.post(
                "/api/ai/llm/chat",
                data=json.dumps({"ingredients": "鸡肉粉, 鱼肉粉, 维生素D"}),
                content_type="application/json",
            )

        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("additive", data)
        self.assertIn("ingredient", data)
        self.assertIn("percent_data", data)

    def test_llm_chat_missing_ingredients(self):
        """测试 LLM 聊天缺少成分"""
        response = self.client.post(
            "/api/ai/llm/chat", data=json.dumps({}), content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)


# 运行测试的命令：
# python manage.py test api.tests
