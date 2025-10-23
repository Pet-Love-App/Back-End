# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    扩展Django默认用户模型
    """

    nickname = models.CharField(max_length=50, blank=True, null=True, verbose_name="昵称")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, verbose_name="头像")
    bio = models.TextField(max_length=500, blank=True, null=True, verbose_name="个人简介")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.nickname or self.username

    class Meta:
        db_table = "users_customuser"
        verbose_name = "用户"
        verbose_name_plural = "用户"


class Comment(models.Model):
    """
    评论模型 - 支持对任何内容的评论
    """

    COMMENT_TYPES = [
        ("additive", "添加剂评论"),
        ("ingredient", "成分评论"),
        ("pet", "宠物评论"),
        ("user", "用户评论"),
        ("general", "一般评论"),
    ]

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="comments", verbose_name="评论用户"
    )
    content = models.TextField(verbose_name="评论内容")
    comment_type = models.CharField(
        max_length=20, choices=COMMENT_TYPES, default="general", verbose_name="评论类型"
    )
    # 使用简单的target_id和target_type来关联任何模型
    target_id = models.PositiveIntegerField(verbose_name="目标ID")
    target_type = models.CharField(max_length=50, verbose_name="目标类型")  # 如 'additive', 'pet'

    # 支持评论回复
    parent_comment = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="replies",
        verbose_name="父评论",
    )

    # 评论状态和统计
    likes_count = models.PositiveIntegerField(default=0, verbose_name="点赞数")
    replies_count = models.PositiveIntegerField(default=0, verbose_name="回复数")
    is_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    is_pinned = models.BooleanField(default=False, verbose_name="是否置顶")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return f"{self.user.nickname or self.user.username}: {self.content[:50]}..."

    @property
    def target_object(self):
        """获取评论的目标对象"""
        try:
            if self.target_type == "additive":
                from additive.models import Additive

                return Additive.objects.get(pk=self.target_id)
            elif self.target_type == "pet":
                from pets.models import Pet

                return Pet.objects.get(pk=self.target_id)
            elif self.target_type == "user":
                return CustomUser.objects.get(pk=self.target_id)
        except:
            return None

    class Meta:
        db_table = "users_comment"
        verbose_name = "评论"
        verbose_name_plural = "评论"
        ordering = ["-is_pinned", "-created_at"]
        indexes = [
            models.Index(fields=["target_type", "target_id"]),
            models.Index(fields=["comment_type"]),
            models.Index(fields=["created_at"]),
        ]


class CommentLike(models.Model):
    """
    评论点赞模型
    """

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="comment_likes", verbose_name="用户"
    )
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="likes", verbose_name="评论"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="点赞时间")

    class Meta:
        db_table = "users_commentlike"
        verbose_name = "评论点赞"
        verbose_name_plural = "评论点赞"
        unique_together = ("user", "comment")  # 防止重复点赞
