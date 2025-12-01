"""
论坛系统模型
包含帖子、帖子媒体、收藏、通知
"""

from django.contrib.auth.models import User
from django.db import models


class Post(models.Model):
    """
    帖子模型
    用户在广场发布的内容，支持文字和媒体文件
    """

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts", help_text="帖子作者"
    )
    content = models.TextField(blank=True, default="", help_text="帖子内容（文字）")
    created_at = models.DateTimeField(auto_now_add=True, help_text="创建时间")
    updated_at = models.DateTimeField(auto_now=True, help_text="更新时间")

    class Meta:
        db_table = "post"
        ordering = ["-created_at"]
        verbose_name = "帖子"
        verbose_name_plural = "帖子"
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["author", "-created_at"]),
        ]

    def __str__(self):
        return f"Post {self.id} by {self.author.username}"

    @property
    def favorites_count(self):
        """获取收藏数量"""
        return self.favorites.count()

    @property
    def comments_count(self):
        """获取评论数量"""
        from comment.models import Comment

        return Comment.objects.filter(target_type="post", target_id=self.id).count()

    def is_favorited_by(self, user):
        """判断是否被指定用户收藏"""
        if not user or not user.is_authenticated:
            return False
        return self.favorites.filter(user=user).exists()


class PostMedia(models.Model):
    """
    帖子媒体模型
    存储帖子中的图片和视频文件
    """

    IMAGE = "image"
    VIDEO = "video"
    TYPE_CHOICES = ((IMAGE, "图片"), (VIDEO, "视频"))

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="media", help_text="所属帖子"
    )
    file = models.FileField(upload_to="post_media/", help_text="媒体文件")
    media_type = models.CharField(max_length=10, choices=TYPE_CHOICES, help_text="媒体类型")
    created_at = models.DateTimeField(auto_now_add=True, help_text="上传时间")

    class Meta:
        db_table = "post_media"
        ordering = ["created_at"]  # 按上传顺序排序
        verbose_name = "帖子媒体"
        verbose_name_plural = "帖子媒体"
        indexes = [
            models.Index(fields=["post", "created_at"]),
        ]

    def __str__(self):
        return f"{self.get_media_type_display()} - {self.post.id}"


class Favorite(models.Model):
    """
    帖子收藏模型
    记录用户收藏的帖子
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="post_favorites", help_text="收藏用户"
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="favorites", help_text="被收藏帖子"
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="收藏时间")

    class Meta:
        db_table = "post_favorite"
        unique_together = ("user", "post")
        ordering = ["-created_at"]
        verbose_name = "帖子收藏"
        verbose_name_plural = "帖子收藏"
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["post"]),
        ]

    def __str__(self):
        return f"{self.user.username} 收藏了帖子 {self.post.id}"


class Notification(models.Model):
    """
    通知模型
    记录用户收到的通知（评论、回复等）
    """

    VERB_CHOICES = [
        ("comment_post", "评论了你的帖子"),
        ("reply_comment", "回复了你的评论"),
    ]

    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications", help_text="接收者"
    )
    actor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notification_actors", help_text="动作发起者"
    )
    verb = models.CharField(max_length=20, choices=VERB_CHOICES, help_text="动作类型")
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        help_text="相关帖子",
    )
    comment = models.ForeignKey(
        "comment.Comment",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="forum_notifications",
        help_text="相关评论",
    )
    unread = models.BooleanField(default=True, help_text="是否未读")
    created_at = models.DateTimeField(auto_now_add=True, help_text="创建时间")

    class Meta:
        db_table = "notification"
        ordering = ["-created_at"]
        verbose_name = "通知"
        verbose_name_plural = "通知"
        indexes = [
            models.Index(fields=["recipient", "-created_at"]),
            models.Index(fields=["recipient", "unread"]),
        ]

    def __str__(self):
        return f"{self.actor.username} {self.get_verb_display()}"

    def mark_as_read(self):
        """标记为已读"""
        if self.unread:
            self.unread = False
            self.save(update_fields=["unread"])
