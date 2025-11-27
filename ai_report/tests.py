import json
from unittest.mock import patch

from django.test import SimpleTestCase, Client


BASE = "/api/ai/llm/chat"


class LLMChatInterfaceTests(SimpleTestCase):
	def setUp(self):
		self.client = Client()

	def test_missing_ingredients_returns_400(self):
		resp = self.client.post(BASE, data=json.dumps({}), content_type="application/json")
		self.assertEqual(resp.status_code, 400)
		j = resp.json()
		# error should be a string
		self.assertIsInstance(j.get("error"), str)

	def test_llm_chat_network_error_returns_502(self):
		with patch("ai_report.views._post_json", return_value=(0, "connection refused")):
			resp = self.client.post(
				BASE,
				data=json.dumps({"ingredients": "鸡肉, 玉米"}),
				content_type="application/json",
			)
			self.assertEqual(resp.status_code, 502)
			j = resp.json()
			self.assertIsInstance(j.get("ok"), bool)
			self.assertIsInstance(j.get("error"), dict)

	def test_llm_chat_parses_provider_json_into_schema(self):
		model_json = {
			"tags": ["成猫粮", "高蛋白"],
			"additives": ["维生素D"],
			"identified_nutrients": ["粗蛋白"],
			"safety": "安全",
			"nutrient": "营养详述",
			"percentage": True,
			"crude_protein": 30,
			"crude_fat": 10,
			"carbohydrates": 40,
			"crude_fiber": 5,
			"crude_ash": 5,
		}

		provider_shape = {"choices": [{"message": {"content": json.dumps(model_json, ensure_ascii=False)}}]}

		with patch("ai_report.views._post_json", return_value=(200, json.dumps(provider_shape, ensure_ascii=False))):
			resp = self.client.post(
				BASE,
				data=json.dumps({"ingredients": "鸡肉, 维生素D"}),
				content_type="application/json",
			)
			self.assertEqual(resp.status_code, 200)
			j = resp.json()

			# Basic structural checks
			self.assertIsInstance(j.get("additive"), list)
			self.assertIsInstance(j.get("ingredient"), list)
			self.assertIsInstance(j.get("nutrient"), str)
			self.assertIsInstance(j.get("safety"), str)
			self.assertIn("percent_data", j)
			pd = j.get("percent_data") or {}
			# numeric fields may be None or float
			for k in ("crude_protein", "crude_fat", "carbohydrates", "crude_fiber", "crude_ash", "others"):
				v = pd.get(k)
				self.assertTrue(v is None or isinstance(v, (int, float)))

			# if percentage is True, sum of parts should be approximately 100
			if j.get("percentage"):
				total = sum([v or 0 for v in (pd.get("crude_protein"), pd.get("crude_fat"), pd.get("carbohydrates"), pd.get("crude_fiber"), pd.get("crude_ash"), pd.get("others"))])
				self.assertAlmostEqual(total, 100, delta=0.5)

	def test_llm_chat_handles_non_json_provider_and_returns_default_schema(self):
		with patch("ai_report.views._post_json", return_value=(200, "plain text without json")):
			resp = self.client.post(
				BASE,
				data=json.dumps({"ingredients": "鸡肉, 玉米"}),
				content_type="application/json",
			)
			self.assertEqual(resp.status_code, 200)
			j = resp.json()
			# Default result should have empty lists and percent_data values None
			self.assertIsInstance(j.get("additive"), list)
			self.assertIsInstance(j.get("ingredient"), list)
			pd = j.get("percent_data") or {}
			self.assertTrue(pd.get("crude_protein") is None)
