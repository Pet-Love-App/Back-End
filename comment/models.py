"""
评论系统模型
支持对不同类型对象（帖子、猫粮、报告等）的评论
"""

from django.contrib.auth.models import User
from django.db import models


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
