import unittest
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory, force_authenticate


class FakeObj:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class FakeQS(list):
    def exists(self):
        return len(self) > 0

    def first(self):
        return self[0] if self else None

    def count(self):
        return len(self)

    def filter(self, *args, **kwargs):  # 支持 Q 对象或常规过滤
        return FakeQS(self)


try:
    from catfood import views
    VIEWS_AVAILABLE = True
except Exception:
    VIEWS_AVAILABLE = False


@unittest.skipUnless(VIEWS_AVAILABLE, "catfood.views not importable")
class CatFoodViewSetTests(SimpleTestCase):
    def setUp(self):
        self.rf = APIRequestFactory()

    def test_list(self):
        fake_a = FakeObj(id=1, name="A", brand="B")
        fake_b = FakeObj(id=2, name="C", brand="D")
        mock_qs = FakeQS([fake_a, fake_b])
        with patch("catfood.views.CatFoodViewSet.get_queryset", return_value=mock_qs), patch(
            "catfood.views.CatFoodViewSet.filter_queryset", return_value=mock_qs
        ), patch("catfood.views.CatFoodViewSet.get_serializer") as mock_get_serializer:
            serializer = MagicMock()
            serializer.data = [
                {"id": 1, "name": "A", "brand": "B"},
                {"id": 2, "name": "C", "brand": "D"},
            ]
            mock_get_serializer.return_value = serializer

            view = views.CatFoodViewSet.as_view({"get": "list"})
            request = self.rf.get("/catfood/")
            resp = view(request)
            self.assertEqual(resp.status_code, 200)
            if isinstance(resp.data, dict):  # 分页情况下
                self.assertIn("results", resp.data)
                self.assertEqual(len(resp.data["results"]), 2)
            else:
                self.assertIsInstance(resp.data, list)
                self.assertEqual(len(resp.data), 2)

    def test_retrieve(self):
        fake = FakeObj(id=10, name="Tuna", brand="X")
        with patch("catfood.views.CatFoodViewSet.get_object", return_value=fake), patch(
            "catfood.views.CatFoodViewSet.get_serializer"
        ) as mock_get_serializer:
            serializer = MagicMock()
            serializer.data = {"id": 10, "name": "Tuna", "brand": "X"}
            mock_get_serializer.return_value = serializer

            view = views.CatFoodViewSet.as_view({"get": "retrieve"})
            request = self.rf.get("/catfood/10/")
            resp = view(request, pk=10)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.data["id"], 10)

    def test_create_success(self):
        created = FakeObj(id=123, name="Kibble", brand="Z")
        with patch("catfood.views.CatFoodViewSet.get_serializer") as mock_get_serializer, patch(
            "catfood.views.CatFoodViewSet.perform_create"
        ) as mock_perform_create, patch("catfood.views.CatFoodSerializer") as MockDetailSerializer:
            create_ser = MagicMock()
            create_ser.is_valid.return_value = True
            create_ser.instance = created
            mock_get_serializer.return_value = create_ser
            mock_perform_create.side_effect = lambda s: None
            detail_ser_instance = MagicMock()
            detail_ser_instance.data = {"id": 123, "name": "Kibble", "brand": "Z"}
            MockDetailSerializer.return_value = detail_ser_instance

            view = views.CatFoodViewSet.as_view({"post": "create"})
            request = self.rf.post(
                "/catfood/", {"name": "Kibble", "brand": "Z"}, format="json"
            )
            resp = view(request)
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(resp.data["id"], 123)

    def test_create_invalid(self):
        class BadSer:
            def is_valid(self, raise_exception=False):
                if raise_exception:
                    raise ValidationError({"name": ["required"]})
                return False
            @property
            def data(self):
                return {}
        with patch("catfood.views.CatFoodViewSet.get_serializer", return_value=BadSer()):
            view = views.CatFoodViewSet.as_view({"post": "create"})
            request = self.rf.post("/catfood/", {}, format="json")
            resp = view(request)
            self.assertEqual(resp.status_code, 400)
            self.assertIn("name", resp.data)

    def test_search_by_name_found(self):
        fake = FakeObj(id=1, name="Chicken", brand="Y")
        mock_qs = FakeQS([fake])
        with patch("catfood.views.CatFoodViewSet.get_queryset", return_value=mock_qs), patch(
            "catfood.views.CatFoodViewSet.filter_queryset", return_value=mock_qs
        ), patch("catfood.views.CatFoodViewSet.get_serializer") as mock_get_serializer:
            ser = MagicMock()
            ser.data = [{"id": 1, "name": "Chicken", "brand": "Y"}]
            mock_get_serializer.return_value = ser

            view = views.CatFoodViewSet.as_view({"get": "search_by_name"})
            request = self.rf.get("/catfood/search/?name=Chicken")
            resp = view(request)
            self.assertEqual(resp.status_code, 200)
            if isinstance(resp.data, dict):
                self.assertIn("results", resp.data)
                self.assertEqual(resp.data["results"][0]["name"], "Chicken")
            else:
                self.assertIsInstance(resp.data, list)
                self.assertEqual(resp.data[0]["name"], "Chicken")

    def test_search_by_name_missing(self):
        view = views.CatFoodViewSet.as_view({"get": "search_by_name"})
        request = self.rf.get("/catfood/search/")
        resp = view(request)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("error", resp.data)

    def test_get_comments(self):
        fake_catfood = FakeObj(id=7)
        fake_c1 = FakeObj(id=1, content="good")
        fake_c2 = FakeObj(id=2, content="ok")
        comments_qs = FakeQS([fake_c1, fake_c2])
        with patch("catfood.views.CatFoodViewSet.get_object", return_value=fake_catfood), patch(
            "catfood.views.Comment"
        ) as MockComment, patch("catfood.views.CommentSerializer") as MockCommentSerializer:
            MockComment.objects.filter.return_value.order_by.return_value = comments_qs

            ser_inst = MagicMock()
            ser_inst.data = [
                {"id": 1, "content": "good"},
                {"id": 2, "content": "ok"},
            ]
            MockCommentSerializer.return_value = ser_inst

            view = views.CatFoodViewSet.as_view({"get": "get_comments"})
            request = self.rf.get("/catfood/7/comments/")
            resp = view(request, pk=7)
            self.assertEqual(resp.status_code, 200)
            if isinstance(resp.data, dict):
                self.assertIn("results", resp.data)
                self.assertEqual(len(resp.data["results"]), 2)
            else:
                self.assertEqual(len(resp.data), 2)


@unittest.skipUnless(VIEWS_AVAILABLE, "catfood.views not importable")
class CatFoodFavoriteViewSetTests(SimpleTestCase):
    def setUp(self):
        self.rf = APIRequestFactory()

    def test_toggle_favorite_missing_id(self):
        view = views.CatFoodFavoriteViewSet.as_view({"post": "toggle_favorite"})
        request = self.rf.post("/catfood/favorites/toggle/", {}, format="json")
        fake_user = FakeObj(id=1, is_authenticated=True)
        force_authenticate(request, user=fake_user)
        resp = view(request)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("error", resp.data)

    def test_toggle_favorite_catfood_not_found(self):
        with patch("catfood.views.CatFood") as MockCF:
            MockCF.DoesNotExist = type("DoesNotExist", (Exception,), {})
            MockCF.objects.get.side_effect = MockCF.DoesNotExist()
            view = views.CatFoodFavoriteViewSet.as_view({"post": "toggle_favorite"})
            request = self.rf.post(
                "/catfood/favorites/toggle/", {"catfood_id": 999}, format="json"
            )
            fake_user = FakeObj(id=1, is_authenticated=True)
            force_authenticate(request, user=fake_user)
            resp = view(request)
            self.assertEqual(resp.status_code, 404)
            self.assertIn("error", resp.data)

    def test_toggle_favorite_add(self):
        with patch("catfood.views.CatFood") as MockCF, patch(
            "catfood.views.CatFoodFavorite"
        ) as MockFav, patch(
            "catfood.views.CatFoodFavoriteViewSet.get_serializer"
        ) as mock_get_serializer:
            catfood = FakeObj(id=5)
            MockCF.objects.get.return_value = catfood
            MockFav.objects.filter.return_value.first.return_value = None

            ser = MagicMock()
            ser.data = {"id": 77, "catfood": 5}
            mock_get_serializer.return_value = ser

            view = views.CatFoodFavoriteViewSet.as_view({"post": "toggle_favorite"})
            request = self.rf.post(
                "/catfood/favorites/toggle/", {"catfood_id": 5}, format="json"
            )
            fake_user = FakeObj(id=1, is_authenticated=True)
            force_authenticate(request, user=fake_user)
            resp = view(request)
            self.assertEqual(resp.status_code, 201)
            self.assertTrue(resp.data.get("is_favorited"))

    def test_toggle_favorite_remove(self):
        with patch("catfood.views.CatFood") as MockCF, patch(
            "catfood.views.CatFoodFavorite"
        ) as MockFav:
            catfood = FakeObj(id=5)
            MockCF.objects.get.return_value = catfood
            existing = FakeObj(id=88)
            existing.delete = MagicMock()
            MockFav.objects.filter.return_value.first.return_value = existing

            view = views.CatFoodFavoriteViewSet.as_view({"post": "toggle_favorite"})
            request = self.rf.post(
                "/catfood/favorites/toggle/", {"catfood_id": 5}, format="json"
            )
            fake_user = FakeObj(id=1, is_authenticated=True)
            force_authenticate(request, user=fake_user)
            resp = view(request)
            self.assertEqual(resp.status_code, 200)
            self.assertFalse(resp.data.get("is_favorited"))
            existing.delete.assert_called_once()

    def test_check_favorite_missing_id(self):
        view = views.CatFoodFavoriteViewSet.as_view({"post": "check_favorite"})
        request = self.rf.post("/catfood/favorites/check/", {}, format="json")
        fake_user = FakeObj(id=1, is_authenticated=True)
        force_authenticate(request, user=fake_user)
        resp = view(request)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("error", resp.data)

    def test_check_favorite_true_and_false(self):
        with patch("catfood.views.CatFoodFavorite") as MockFav:
            view = views.CatFoodFavoriteViewSet.as_view({"post": "check_favorite"})
            request = self.rf.post(
                "/catfood/favorites/check/", {"catfood_id": 3}, format="json"
            )
            fake_user = FakeObj(id=1, is_authenticated=True)
            force_authenticate(request, user=fake_user)

            MockFav.objects.filter.return_value.exists.return_value = True
            resp = view(request)
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(resp.data.get("is_favorited"))

            MockFav.objects.filter.return_value.exists.return_value = False
            request2 = self.rf.post(
                "/catfood/favorites/check/", {"catfood_id": 3}, format="json"
            )
            force_authenticate(request2, user=fake_user)
            resp2 = view(request2)
            self.assertEqual(resp2.status_code, 200)
            self.assertFalse(resp2.data.get("is_favorited"))


if __name__ == "__main__":
    unittest.main()
