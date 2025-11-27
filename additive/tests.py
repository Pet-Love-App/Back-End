from django.test import SimpleTestCase, RequestFactory
from unittest.mock import patch, MagicMock
import json

from . import views


class FakeObj:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class FakeQS:
    def __init__(self, items):
        self._items = list(items)

    def exists(self):
        return bool(self._items)

    def count(self):
        return len(self._items)

    def first(self):
        return self._items[0] if self._items else None

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, s):
        return self._items[s]


# A real exception class to attach to mocked models so
# `except Additive.DoesNotExist:` works correctly in views.
class DoesNotExist(Exception):
    pass


class AdditiveViewsTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_search_additive_no_query(self):
        req = self.factory.get("/", {})
        resp = views.search_additive(req)
        self.assertEqual(resp.status_code, 400)

    @patch("additive.views.Additive")
    def test_search_additive_exact(self, mock_additive_model):
        fake = FakeObj(id=1, name="盐", en_name="Salt", applicable_range="食品", type="调味")
        mock_manager = MagicMock()
        mock_manager.objects.get.return_value = fake
        # ensure DoesNotExist on the mock is an Exception subclass
        mock_additive_model.DoesNotExist = DoesNotExist
        mock_additive_model.objects = mock_manager.objects

        req = self.factory.get("/", {"name": "盐"})
        resp = views.search_additive(req)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode())
        self.assertEqual(data["match_type"], "exact")
        self.assertEqual(data["additive"]["name"], "盐")

    @patch("additive.views.Additive")
    def test_search_additive_fuzzy_single(self, mock_additive_model):
        # get() raises DoesNotExist
        mock_manager = MagicMock()
        # attach a real exception class to the mock so views can `except` it
        mock_additive_model.DoesNotExist = DoesNotExist
        mock_manager.objects.get.side_effect = mock_additive_model.DoesNotExist
        fake = FakeObj(id=2, name="糖", en_name="Sugar", applicable_range="食品", type="甜味")
        mock_manager.objects.filter.return_value = FakeQS([fake])
        mock_additive_model.objects = mock_manager.objects

        req = self.factory.get("/", {"name": "糖"})
        resp = views.search_additive(req)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode())
        self.assertEqual(data["match_type"], "fuzzy_single")
        self.assertEqual(data["additive"]["name"], "糖")

    @patch("additive.views.Additive")
    def test_search_additive_fuzzy_multiple(self, mock_additive_model):
        mock_manager = MagicMock()
        mock_additive_model.DoesNotExist = DoesNotExist
        mock_manager.objects.get.side_effect = mock_additive_model.DoesNotExist
        fake1 = FakeObj(id=3, name="酸A", en_name="A", applicable_range="食品", type="酸")
        fake2 = FakeObj(id=4, name="酸B", en_name="B", applicable_range="食品", type="酸")
        mock_manager.objects.filter.return_value = FakeQS([fake1, fake2])
        mock_additive_model.objects = mock_manager.objects

        req = self.factory.get("/", {"name": "酸"})
        resp = views.search_additive(req)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode())
        self.assertEqual(data["match_type"], "fuzzy_multiple")
        self.assertIn("additives", data)


class IngredientViewsTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_search_ingredient_no_query(self):
        req = self.factory.get("/", {})
        resp = views.search_ingredient(req)
        self.assertEqual(resp.status_code, 400)

    @patch("additive.views.Ingredient")
    def test_search_ingredient_exact(self, mock_ingredient_model):
        fake = FakeObj(id=10, name="维生素C", type="维生素", label="VC", desc="抗氧化")
        mock_manager = MagicMock()
        mock_manager.objects.get.return_value = fake
        mock_ingredient_model.objects = mock_manager.objects

        req = self.factory.get("/", {"name": "维生素C"})
        resp = views.search_ingredient(req)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode())
        self.assertEqual(data["match_type"], "exact")
        self.assertEqual(data["ingredient"]["name"], "维生素C")

    @patch("additive.views.Ingredient")
    def test_add_ingredient_missing_name(self, mock_ingredient_model):
        req = self.factory.post("/", data=json.dumps({}), content_type="application/json")
        resp = views.add_ingredient(req)
        self.assertEqual(resp.status_code, 400)

    @patch("additive.views.Ingredient")
    def test_add_ingredient_conflict(self, mock_ingredient_model):
        mock_manager = MagicMock()
        mock_manager.objects.filter.return_value.exists.return_value = True
        mock_ingredient_model.objects = mock_manager.objects

        payload = {"name": "已有成分", "type": "x", "label": "L", "desc": "d"}
        req = self.factory.post("/", data=json.dumps(payload), content_type="application/json")
        resp = views.add_ingredient(req)
        self.assertEqual(resp.status_code, 409)

    @patch("additive.views.Ingredient")
    def test_add_ingredient_success(self, mock_ingredient_model):
        mock_manager = MagicMock()
        mock_manager.objects.filter.return_value.exists.return_value = False
        fake_created = FakeObj(id=11, name="新成分", type="t", label="L", desc="d")
        mock_manager.objects.create.return_value = fake_created
        mock_ingredient_model.objects = mock_manager.objects

        payload = {"name": "新成分", "type": "t", "label": "L", "desc": "d"}
        req = self.factory.post("/", data=json.dumps(payload), content_type="application/json")
        resp = views.add_ingredient(req)
        self.assertEqual(resp.status_code, 201)
        data = json.loads(resp.content.decode())
        self.assertEqual(data["ingredient"]["name"], "新成分")

