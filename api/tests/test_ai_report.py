"""
AI 报告 API 测试

测试 LLM 聊天、报告保存、报告获取等功能。
"""

import json
from unittest.mock import Mock, patch

from django.test import Client, TestCase

from .helpers import FakeSupabaseResponse, FakeUser


class AIReportAPITests(TestCase):
    """AI 报告 API 测试"""

    def setUp(self):
        """测试前准备"""
        self.client = Client()

    @patch("api.ai_report_views.requests.post")
    def test_llm_chat_success(self, mock_post):
        """测试 LLM 聊天成功"""
        # Arrange
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
                                "protein": 30.0,
                                "fat": 10.0,
                                "carbohydrates": 40.0,
                                "fiber": 5.0,
                                "ash": 5.0,
                            }
                        )
                    }
                }
            ]
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps(ai_response)
        mock_post.return_value = mock_response

        # Act
        response = self.client.post(
            "/api/ai/llm/chat/",
            data=json.dumps({"ingredients": "鸡肉粉, 鱼肉粉, 维生素D"}),
            content_type="application/json",
        )

        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("additive", data)
        self.assertIn("ingredient", data)
        self.assertIn("percent_data", data)
        self.assertIsInstance(data["additive"], list)
        self.assertIsInstance(data["ingredient"], list)

    def test_llm_chat_missing_ingredients(self):
        """测试 LLM 聊天缺少成分"""
        # Act
        response = self.client.post(
            "/api/ai/llm/chat/", data=json.dumps({}), content_type="application/json"
        )

        # Assert
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)

    @patch("api.ai_report_views.supabase_admin")
    @patch("middleware.supabase_auth.get_current_user")
    def test_save_report(self, mock_user, mock_admin):
        """测试保存 AI 报告"""
        # Arrange
        mock_user.return_value = FakeUser()
        mock_admin.table.return_value.insert.return_value.execute.return_value = (
            FakeSupabaseResponse(
                data=[{"id": 1, "catfood_id": 1, "user_id": "test-uuid"}]
            )
        )

        # Act
        response = self.client.post(
            "/api/ai/save/",
            data=json.dumps(
                {
                    "catfood_id": 1,
                    "percent_data": {
                        "crude_protein": 30.0,
                        "crude_fat": 15.0,
                    },
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer test-token",
        )

        # Assert
        self.assertEqual(response.status_code, 200)

    @patch("api.ai_report_views.supabase_admin")
    def test_get_report(self, mock_admin):
        """测试获取 AI 报告"""
        # Arrange
        mock_result = FakeSupabaseResponse(
            data=[
                {
                    "id": 1,
                    "catfood_id": 1,
                    "percent_data": {"crude_protein": 30.0, "crude_fat": 15.0},
                    "catfood": {"id": 1, "name": "测试猫粮"},
                }
            ]
        )

        mock_admin.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_result

        # Act
        response = self.client.get("/api/ai/1/")

        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("report", data)
