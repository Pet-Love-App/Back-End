"""
AI分析报告模型
用于保存猫粮的AI分析报告，避免重复调用LLM
"""

from django.contrib.auth.models import User
from django.db import models


class AIAnalysisReport(models.Model):
    """
    AI分析报告模型
    存储对猫粮配料表的AI分析结果
    """

    # 关联的猫粮（一对一关系，每个猫粮只有一份最新的报告）
    catfood = models.OneToOneField(
        "catfood.CatFood",
        on_delete=models.CASCADE,
        related_name="ai_report",
        help_text="关联的猫粮",
    )

    # 原始输入
    ingredients_text = models.TextField(help_text="原始配料表文本")

    # 分析结果 - 标签
    tags = models.JSONField(default=list, help_text="产品标签列表")

    # 分析结果 - 添加剂
    additives = models.JSONField(default=list, help_text="识别到的添加剂列表")

    # 分析结果 - 营养成分
    ingredients = models.JSONField(default=list, help_text="识别到的营养成分列表")

    # 分析结果 - 安全性分析
    safety = models.TextField(blank=True, help_text="安全性分析文本")

    # 分析结果 - 营养分析
    nutrient = models.TextField(blank=True, help_text="营养分析文本")

    # 分析结果 - 百分比分析
    percentage = models.BooleanField(default=False, help_text="是否支持百分比分析")

    crude_protein = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, help_text="粗蛋白含量（%）"
    )

    crude_fat = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, help_text="粗脂肪含量（%）"
    )

    carbohydrates = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, help_text="碳水化合物含量（%）"
    )

    crude_fiber = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, help_text="粗纤维含量（%）"
    )

    crude_ash = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, help_text="粗灰分含量（%）"
    )

    others = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, help_text="其他成分含量（%）"
    )

    # 元数据
    created_at = models.DateTimeField(auto_now_add=True, help_text="创建时间")

    updated_at = models.DateTimeField(auto_now=True, help_text="更新时间")

    class Meta:
        db_table = "ai_analysis_report"
        verbose_name = "AI分析报告"
        verbose_name_plural = "AI分析报告"
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["catfood"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"AI报告 - {self.catfood.name if self.catfood else 'Unknown'}"


class FavoriteReport(models.Model):
    """
    AI报告收藏模型
    用户可以收藏感兴趣的AI分析报告
    """

    # 关联的用户
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favorite_reports", help_text="收藏用户"
    )

    # 关联的AI报告
    report = models.ForeignKey(
        AIAnalysisReport,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        help_text="收藏的AI报告",
    )

    # 元数据
    created_at = models.DateTimeField(auto_now_add=True, help_text="收藏时间")

    class Meta:
        db_table = "favorite_report"
        verbose_name = "AI报告收藏"
        verbose_name_plural = "AI报告收藏"
        unique_together = [["user", "report"]]  # 一个用户对同一个报告只能收藏一次
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["report"]),
        ]

    def __str__(self):
        return f"{self.user.username} 收藏了 {self.report}"
