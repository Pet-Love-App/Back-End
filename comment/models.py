"""
评论系统模型
"""

from django.contrib.auth.models import User
from django.db import models


class Post(models.Model):
    """帖子模型（广场 / 用户发布内容）"""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts", help_text="帖子作者")
    content = models.TextField(blank=True, default="", help_text="帖子内容（文字）")
    created_at = models.DateTimeField(auto_now_add=True, help_text="创建时间")
    updated_at = models.DateTimeField(auto_now=True, help_text="更新时间")

    class Meta:
        db_table = "post"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post {self.id} by {self.author.username}"


class PostMedia(models.Model):
    """帖子媒体（图片 / 视频）"""
    IMAGE = "image"
    VIDEO = "video"
    TYPE_CHOICES = ((IMAGE, "图片"), (VIDEO, "视频"))

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="media", help_text="所属帖子")
    file = models.FileField(upload_to="post_media/", help_text="媒体文件")
    media_type = models.CharField(max_length=10, choices=TYPE_CHOICES, help_text="媒体类型")
    created_at = models.DateTimeField(auto_now_add=True, help_text="上传时间")

    class Meta:
        db_table = "post_media"
        ordering = ["-created_at"]

    def __str__(self):
        return f"PostMedia {self.id} ({self.media_type})"


class Favorite(models.Model):
    """帖子收藏"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_favorites", help_text="收藏用户")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="favorites", help_text="被收藏帖子")
    created_at = models.DateTimeField(auto_now_add=True, help_text="收藏时间")

    class Meta:
        db_table = "post_favorite"
        unique_together = ("user", "post")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} 收藏 {self.post.id}"


class Notification(models.Model):
    """消息通知：有人评论我的帖子 / 回复我的评论"""
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications", help_text="接收者")
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_actors", help_text="动作发起者")
    verb = models.CharField(max_length=20, help_text="动作类型 comment_post / reply_comment")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications", help_text="相关帖子")
    comment = models.ForeignKey("Comment", on_delete=models.CASCADE, null=True, blank=True, related_name="notifications", help_text="相关评论")
    unread = models.BooleanField(default=True, help_text="是否未读")
    created_at = models.DateTimeField(auto_now_add=True, help_text="创建时间")

    class Meta:
        db_table = "notification"
        ordering = ["-created_at"]

    def __str__(self):
        return f"通知 {self.id} to {self.recipient.username} {self.verb} by {self.actor.username}"


class Comment(models.Model):
    """
    评论模型
    支持对不同类型对象（帖子、猫粮、报告等）的评论 + 支持父评论（回复）
    """

    TARGET_TYPE_CHOICES = [
        ("post", "帖子"),
        ("catfood", "猫粮"),
        ("report", "报告"),
    ]

    # 评论内容
    content = models.TextField(help_text="评论内容")

    # 评论作者（关联到 Django User）
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        help_text="评论作者",
    )

    # 关联的目标对象
    target_type = models.CharField(
        max_length=20,
        choices=TARGET_TYPE_CHOICES,
        help_text="目标对象类型",
    )
    target_id = models.IntegerField(help_text="目标对象 ID")

    # 父评论（回复时使用）
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="replies",
        on_delete=models.CASCADE,
        help_text="父评论（若为回复）",
    )

    # 点赞数（冗余字段，配合 CommentLike）
    likes = models.IntegerField(default=0, help_text="点赞数")

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, help_text="创建时间")
    updated_at = models.DateTimeField(auto_now=True, help_text="更新时间")

    class Meta:
        db_table = "comment"
        verbose_name = "评论"
        verbose_name_plural = "评论"
        ordering = ["-created_at"]  # 按创建时间倒序
        indexes = [
            models.Index(fields=["target_type", "target_id"]),
            models.Index(fields=["author"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}"


class CommentLike(models.Model):
    """
    评论点赞记录
    记录哪个用户点赞了哪条评论
    """

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="like_records",
        help_text="评论",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comment_likes",
        help_text="点赞用户",
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="点赞时间")

    class Meta:
        db_table = "comment_like"
        verbose_name = "评论点赞"
        verbose_name_plural = "评论点赞"
        unique_together = [["comment", "user"]]  # 一个用户只能点赞一次
        indexes = [
            models.Index(fields=["comment", "user"]),
        ]

    def __str__(self):
        return f"{self.user.username} liked {self.comment.id}"
