import json
from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase

from api_search.views import ingredient_info

class IngredientInfoViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _post(self, body_bytes: bytes):
        return self.factory.post("/ingredient_info", data=body_bytes, content_type="application/json")

    def test_missing_ingredient_returns_400(self):
        req = self._post(json.dumps({}).encode("utf-8"))
        resp = ingredient_info(req)
        self.assertEqual(resp.status_code, 400)
        j = json.loads(resp.content.decode("utf-8"))
        self.assertEqual(j.get("error", {}).get("code"), "missing_ingredient")

    def test_bad_json_returns_400(self):
        # invalid JSON
        req = self._post(b"{ invalid json")
        resp = ingredient_info(req)
        self.assertEqual(resp.status_code, 400)
        j = json.loads(resp.content.decode("utf-8"))
        self.assertEqual(j.get("error", {}).get("code"), "bad_json")

    def test_network_error_returns_502(self):
        with patch("api_search.views._fetch_summary", return_value=(0, "connection failed")):
            req = self._post(json.dumps({"ingredient": "维生素D"}).encode("utf-8"))
            resp = ingredient_info(req)
            self.assertEqual(resp.status_code, 502)
            j = json.loads(resp.content.decode("utf-8"))
            self.assertEqual(j.get("error", {}).get("code"), "network")

    def test_invalid_string_response_returns_502(self):
        with patch("api_search.views._fetch_summary", return_value=(200, "not-a-dict")):
            req = self._post(json.dumps({"ingredient": "玉米"}).encode("utf-8"))
            resp = ingredient_info(req)
            self.assertEqual(resp.status_code, 502)
            j = json.loads(resp.content.decode("utf-8"))
            self.assertEqual(j.get("error", {}).get("code"), "invalid_response")

    def test_successful_dict_response_returns_200(self):
        fake_data = {"title": "玉米", "result": {"summary": "一种常见的谷物"}}
        with patch("api_search.views._fetch_summary", return_value=(200, fake_data)):
            req = self._post(json.dumps({"ingredient": "玉米"}).encode("utf-8"))
            resp = ingredient_info(req)
            self.assertEqual(resp.status_code, 200)
            j = json.loads(resp.content.decode("utf-8"))
            self.assertTrue(j.get("ok"))
            self.assertEqual(j.get("title"), "玉米")
            self.assertEqual(j.get("extract"), "一种常见的谷物")
