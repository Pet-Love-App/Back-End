from tempfile import mkdtemp
import shutil
import os

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Post, PostMedia, Favorite, Comment, CommentLike, Notification

TEMP_MEDIA_ROOT = mkdtemp()
DB_PATH = os.path.join(TEMP_MEDIA_ROOT, "test.sqlite3")

@override_settings(
    MEDIA_ROOT=TEMP_MEDIA_ROOT,
    ROOT_URLCONF="comment.urls",
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": DB_PATH,
        }
    },
)
class CommentAppAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username="u1", password="p1")
        cls.user2 = User.objects.create_user(username="u2", password="p2")
        cls.user3 = User.objects.create_user(username="u3", password="p3")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.client = APIClient()

    def auth(self, user):
        self.client.force_authenticate(user=user)

    def test_post_create_with_media_and_list(self):
        self.auth(self.user1)
        url = reverse("post-list")
        img = SimpleUploadedFile("img.jpg", b"fake-image-content", content_type="image/jpeg")
        res = self.client.post(url, data={"content": "hello world", "media": [img]}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.author, self.user1)
        self.assertEqual(PostMedia.objects.filter(post=post).count(), 1)

        # random / latest 列表
        res_random = self.client.get(url + "?order=random")
        self.assertEqual(res_random.status_code, status.HTTP_200_OK)
        res_latest = self.client.get(url + "?order=latest")
        self.assertEqual(res_latest.status_code, status.HTTP_200_OK)

    def test_favorite_toggle_and_favorites_list(self):
        # 准备帖子
        post = Post.objects.create(author=self.user1, content="p")
        self.auth(self.user2)

        # 收藏
        fav_url = reverse("post-favorite", kwargs={"pk": post.id})
        res1 = self.client.post(fav_url)
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertIn(res1.data.get("action"), ["favorited", "unfavorited"])
        self.assertTrue(Favorite.objects.filter(user=self.user2, post=post).exists())

        # 取消收藏
        res2 = self.client.post(fav_url)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertFalse(Favorite.objects.filter(user=self.user2, post=post).exists())

        # 再收藏并检查“我的收藏”列表
        self.client.post(fav_url)
        fav_list_url = reverse("post-favorites")
        res3 = self.client.get(fav_list_url)
        self.assertEqual(res3.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res3.data) >= 1)

    def test_comment_create_triggers_notifications(self):
        post = Post.objects.create(author=self.user1, content="p")
        # user2 评论 user1 的帖子 -> 通知给 user1
        self.auth(self.user2)
        create_url = reverse("comment-list")
        res = self.client.post(
            create_url,
            data={"content": "c1", "target_type": "post", "target_id": post.id},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.filter(recipient=self.user1).count(), 1)
        n1 = Notification.objects.filter(recipient=self.user1).first()
        self.assertEqual(n1.verb, "comment_post")

        # user1 回复 user2 的评论 -> 通知给 user2
        parent = Comment.objects.first()
        self.auth(self.user1)
        res2 = self.client.post(
            create_url,
            data={"content": "reply", "target_type": "post", "target_id": post.id, "parent": parent.id},
            format="json",
        )
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.filter(recipient=self.user2, verb="reply_comment").count(), 1)

        # 自己给自己评论不应产生通知
        self.auth(self.user1)
        res3 = self.client.post(
            create_url,
            data={"content": "self", "target_type": "post", "target_id": post.id},
            format="json",
        )
        self.assertEqual(res3.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.filter(recipient=self.user1, verb="comment_post").count(), 1)  # 仍为1

    def test_comment_like_and_order_by_likes(self):
        post = Post.objects.create(author=self.user1, content="p")
        c1 = Comment.objects.create(content="a", author=self.user2, target_type="post", target_id=post.id)
        c2 = Comment.objects.create(content="b", author=self.user3, target_type="post", target_id=post.id)

        # user1 点赞 c2
        self.auth(self.user1)
        like_url = reverse("comment-like", kwargs={"pk": c2.id})
        res = self.client.post(like_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        c2.refresh_from_db()
        self.assertEqual(c2.likes, 1)

        # 列表按点赞排序，c2 应该在前
        list_url = reverse("comment-list")
        res2 = self.client.get(list_url, {"target_type": "post", "target_id": post.id, "order_by": "likes"})
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in res2.data]
        self.assertEqual(ids[0], c2.id)

        # 再次点赞即取消
        res3 = self.client.post(like_url)
        self.assertEqual(res3.status_code, status.HTTP_200_OK)
        c2.refresh_from_db()
        self.assertEqual(c2.likes, 0)

    def test_notifications_read_and_read_all(self):
        # 造一条通知
        post = Post.objects.create(author=self.user1, content="p")
        c = Comment.objects.create(content="a", author=self.user2, target_type="post", target_id=post.id)
        Notification.objects.create(recipient=self.user1, actor=self.user2, verb="comment_post", post=post, comment=c)

        self.auth(self.user1)
        list_url = reverse("notification-list")
        res = self.client.get(list_url, {"unread": "true"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data), 1)

        # 标记单条已读
        nid = res.data[0]["id"]
        read_url = reverse("notification-read", kwargs={"pk": nid})
        res2 = self.client.post(read_url)
        self.assertEqual(res2.status_code, status.HTTP_204_NO_CONTENT)

        # 全部设为已读
        read_all_url = reverse("notification-read-all")
        res3 = self.client.post(read_all_url)
        self.assertEqual(res3.status_code, status.HTTP_204_NO_CONTENT)