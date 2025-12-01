from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import JSONField
User = settings.AUTH_USER_MODEL

class ReputationSummary(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="reputation")
    score = models.IntegerField(default=0, db_index=True)
    profile_completeness = models.IntegerField(default=0)
    review_quality = models.IntegerField(default=0)
    community_contribution = models.IntegerField(default=0)
    compliance = models.IntegerField(default=0)
    level = models.CharField(max_length=32, default="novice", db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reputation_summary"
        verbose_name = "信誉概览"
        verbose_name_plural = "信誉概览"

    def __str__(self):
        return f"Reputation of {self.user}: {self.score}"

class Badge(models.Model):
    """
    定义徽章类型，如：
    code: reply_master
    name: 回信大人
    description: 积极回答问题，评论获赞较多
    """
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True)
    icon = models.CharField(max_length=255, blank=True)  # 可选：存图标URL或类名
    enabled = models.BooleanField(default=True)
    rule = JSONField(blank=True, null=True)
    class Meta:
        db_table = "badge"
        verbose_name = "徽章"
        verbose_name_plural = "徽章"

    def __str__(self):
        return f"{self.name}({self.code})"

class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_badges")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="owners")
    acquired_at = models.DateTimeField(auto_now_add=True)
    is_equipped = models.BooleanField(default=False)  # 是否佩戴

    class Meta:
        db_table = "user_badge"
        verbose_name = "用户徽章"
        verbose_name_plural = "用户徽章"
        unique_together = [["user", "badge"]]

    def __str__(self):
        return f"{self.user} - {self.badge.name} - equipped={self.is_equipped}"

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_reputation_summary(sender, instance, created, **kwargs):
    if created:
        ReputationSummary.objects.create(user=instance)