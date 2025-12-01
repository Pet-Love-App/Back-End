from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase

from django.contrib.auth.models import User

from .models import Post, Notification


class ForumPostTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username="u1", password="pass")
        self.user2 = User.objects.create_user(username="u2", password="pass")

        # 两条帖子，user1 先发，user2 后发
        self.post1 = Post.objects.create(author=self.user1, content="first")
        self.post2 = Post.objects.create(author=self.user2, content="second")

    def test_list_posts_order_and_fields(self):
        resp = self.client.get(reverse("post-list"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        # 视图返回列表（可能被分页）
        if isinstance(data, dict) and "results" in data:
            results = data["results"]
        else:
            results = data

        self.assertGreaterEqual(len(results), 2)
        # post2 出现在 post1 之前
        ids = [r["id"] for r in results]
        self.assertTrue(ids.index(self.post2.id) < ids.index(self.post1.id))
        # 检查常用字段
        item = next(r for r in results if r["id"] == self.post1.id)
        self.assertIn("favorites_count", item)
        self.assertIn("comments_count", item)

    def test_retrieve_post(self):
        resp = self.client.get(reverse("post-detail", args=[self.post1.id]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(data["id"], self.post1.id)
        self.assertEqual(data["content"], "first")

    def test_create_post_permission_and_validation(self):
        # 未认证无法创建
        resp = self.client.post(reverse("post-list"), {"content": ""})
        self.assertIn(resp.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

        # 认证但内容无效
        self.client.force_authenticate(self.user1)
        resp = self.client.post(reverse("post-list"), {"content": "   "})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # 有效创建
        resp = self.client.post(reverse("post-list"), {"content": "Hello forum"})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        from .models import Post as _Post
        self.assertTrue(_Post.objects.filter(author=self.user1, content="Hello forum").exists())

    def test_delete_permissions(self):
        # user2 不能删除 user1 的帖子
        self.client.force_authenticate(self.user2)
        resp = self.client.delete(reverse("post-detail", args=[self.post1.id]))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # author 可以删除
        self.client.force_authenticate(self.user1)
        resp = self.client.delete(reverse("post-detail", args=[self.post1.id]))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_favorite_toggle_and_favorites_list(self):
        # user1 收藏 post2
        self.client.force_authenticate(self.user1)
        resp = self.client.post(reverse("post-favorite", args=[self.post2.id]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(data.get("action"), "favorited")
        self.assertTrue(data.get("is_favorited"))

        # 收藏列表包含 post2
        resp = self.client.get(reverse("post-favorites"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        if isinstance(data, dict) and "results" in data:
            results = data["results"]
        else:
            results = data
        self.assertTrue(any(p["id"] == self.post2.id for p in results))

        # 再次调用切换为取消收藏
        resp = self.client.post(reverse("post-favorite", args=[self.post2.id]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(data.get("action"), "unfavorited")


class NotificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username="u1", password="pass")
        self.user2 = User.objects.create_user(username="u2", password="pass")

        # 创建帖子与通知
        post = Post.objects.create(author=self.user2, content="npost")
        Notification.objects.create(
            recipient=self.user1, actor=self.user2, verb="comment_post", post=post
        )
        Notification.objects.create(
            recipient=self.user1, actor=self.user2, verb="comment_post", post=post, unread=False
        )

    def test_list_and_unread_filter(self):
        self.client.force_authenticate(self.user1)
        resp = self.client.get(reverse("notification-list"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        if isinstance(data, dict) and "results" in data:
            results = data["results"]
        else:
            results = data
        self.assertGreaterEqual(len(results), 2)

        # 仅未读
        resp = self.client.get(reverse("notification-list") + "?unread=true")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        if isinstance(data, dict) and "results" in data:
            results = data["results"]
        else:
            results = data
        # 只有一条未读
        self.assertEqual(len(results), 1)

    def test_mark_read_and_permissions(self):
        n = Notification.objects.filter(recipient=self.user1).first()

        # 非接收者不能标记
        self.client.force_authenticate(self.user2)
        resp = self.client.post(reverse("notification-mark-read", args=[n.id]))
        self.assertIn(resp.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))

        # 接收者可以标记
        self.client.force_authenticate(self.user1)
        resp = self.client.post(reverse("notification-mark-read", args=[n.id]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        n.refresh_from_db()
        self.assertFalse(n.unread)

    def test_mark_all_read_and_unread_count(self):
        self.client.force_authenticate(self.user1)
        resp = self.client.post(reverse("notification-mark-all-read"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # unread_count 应为 0
        resp = self.client.get(reverse("notification-unread-count"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json().get("count"), 0)