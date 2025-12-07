"""
搜索服务 API 测试

测试百度百科成分信息搜索功能
"""

import json
from unittest.mock import Mock, patch

from django.test import Client, TestCase


class SearchAPITests(TestCase):
    """搜索服务 API 测试"""

    def setUp(self):
        """测试前准备"""
        self.client = Client()

    @patch("api.services.search_service.requests.get")
    def test_search_ingredient_success_post(self, mock_get):
        """测试搜索成分信息成功（POST 请求）"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "维生素D",
            "result": {"summary": "维生素D是一种脂溶性维生素..."},
        }
        mock_get.return_value = mock_response

        # Act
        response = self.client.post(
            "/api/search/ingredient/info",
            json.dumps({"ingredient": "维生素D"}),
            content_type="application/json",
        )

        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["data"]["title"], "维生素D")
        self.assertIn("维生素D", data["data"]["extract"])

    @patch("api.services.search_service.requests.get")
    def test_search_ingredient_success_get(self, mock_get):
        """测试搜索成分信息成功（GET 请求）"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "牛磺酸",
            "result": {"summary": "牛磺酸是一种氨基酸..."},
        }
        mock_get.return_value = mock_response

        # Act
        response = self.client.get("/api/search/ingredient/info?q=牛磺酸")

        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["data"]["title"], "牛磺酸")

    def test_search_ingredient_missing_param(self):
        """测试搜索成分信息缺少参数"""
        # Act
        response = self.client.post(
            "/api/search/ingredient/info",
            json.dumps({}),
            content_type="application/json",
        )

        # Assert
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["ok"])
        self.assertIn("ingredient", data["error"]["detail"])

    def test_search_ingredient_invalid_json(self):
        """测试搜索成分信息无效 JSON"""
        # Act
        response = self.client.post(
            "/api/search/ingredient/info",
            "invalid json",
            content_type="application/json",
        )

        # Assert
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["ok"])
        self.assertEqual(data["error"]["code"], "invalid_json")

    @patch("api.services.search_service.requests.get")
    def test_search_ingredient_api_error(self, mock_get):
        """测试搜索成分信息 API 错误"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Act
        response = self.client.post(
            "/api/search/ingredient/info",
            json.dumps({"ingredient": "不存在的成分"}),
            content_type="application/json",
        )

        # Assert
        self.assertEqual(response.status_code, 502)
        data = response.json()
        self.assertFalse(data["ok"])

    @patch("api.services.search_service.requests.get")
    def test_search_ingredient_timeout(self, mock_get):
        """测试搜索成分信息超时"""
        # Arrange
        import requests

        mock_get.side_effect = requests.Timeout()

        # Act
        response = self.client.post(
            "/api/search/ingredient/info",
            json.dumps({"ingredient": "维生素D"}),
            content_type="application/json",
        )

        # Assert
        self.assertEqual(response.status_code, 502)
        data = response.json()
        self.assertFalse(data["ok"])

    @patch("api.services.search_service.SearchService.is_configured")
    def test_search_ingredient_not_configured(self, mock_configured):
        """测试搜索服务未配置"""
        # Arrange
        mock_configured.return_value = False

        # Act
        response = self.client.post(
            "/api/search/ingredient/info",
            json.dumps({"ingredient": "维生素D"}),
            content_type="application/json",
        )

        # Assert
        self.assertEqual(response.status_code, 503)
        data = response.json()
        self.assertFalse(data["ok"])
        self.assertEqual(data["error"]["code"], "service_not_configured")
