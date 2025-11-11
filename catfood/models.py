"""
猫粮相关模型
"""

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class CatFood(models.Model):
    """
    猫粮模型
    包含猫粮的基本信息、营养成分、添加剂等
    """

    # 基本信息
    name = models.CharField(max_length=200, help_text="猫粮名称")
    brand = models.CharField(max_length=100, blank=True, help_text="品牌名称")
    desc = models.TextField(help_text="猫粮简介描述")

    # 图片
    image_url = models.URLField(blank=True, null=True, help_text="猫粮图片URL")

    # 评分信息
    score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="用户总分（0-5分）",
    )
    count_num = models.IntegerField(default=0, help_text="打分人数")

    # 营养成分百分比（干物质基础）
    percentage = models.BooleanField(default=False, help_text="能否生成图表作定量分析")
    crude_protein = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="粗蛋白含量（%）",
    )
    crude_fat = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="粗脂肪含量（%）",
    )
    carbohydrates = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="碳水化合物含量（%）",
    )
    crude_fiber = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="粗纤维含量（%）",
    )
    crude_ash = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="粗灰分含量（%）",
    )
    others = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="其他成分含量（%）",
    )

    # 分析内容
    safety = models.TextField(blank=True, help_text="安全性分析")
    nutrient = models.TextField(blank=True, help_text="营养分析")

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, help_text="创建时间")
    updated_at = models.DateTimeField(auto_now=True, help_text="更新时间")

    class Meta:
        db_table = "catfood"
        verbose_name = "猫粮"
        verbose_name_plural = "猫粮"
        ordering = ["-score", "-created_at"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["brand"]),
            models.Index(fields=["-score"]),
        ]

    def __str__(self):
        return f"{self.brand} - {self.name}" if self.brand else self.name


class CatFoodTag(models.Model):
    """
    猫粮标签模型
    如：成猫粮、幼猫粮、全阶段、高蛋白、易消化、无谷配方等
    """

    name = models.CharField(max_length=50, unique=True, help_text="标签名称")
    description = models.TextField(blank=True, help_text="标签描述")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "catfood_tag"
        verbose_name = "猫粮标签"
        verbose_name_plural = "猫粮标签"

    def __str__(self):
        return self.name


class CatFoodTagRelation(models.Model):
    """
    猫粮和标签的多对多关系表
    """

    catfood = models.ForeignKey(
        CatFood,
        on_delete=models.CASCADE,
        related_name="tag_relations",
    )
    tag = models.ForeignKey(
        CatFoodTag,
        on_delete=models.CASCADE,
        related_name="catfood_relations",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "catfood_tag_relation"
        unique_together = [["catfood", "tag"]]
        verbose_name = "猫粮标签关系"
        verbose_name_plural = "猫粮标签关系"

    def __str__(self):
        return f"{self.catfood.name} - {self.tag.name}"


class CatFoodIngredient(models.Model):
    """
    猫粮营养成分关系表
    关联猫粮和营养成分（Ingredient）
    """

    catfood = models.ForeignKey(
        CatFood,
        on_delete=models.CASCADE,
        related_name="ingredients",
    )
    ingredient = models.ForeignKey(
        "additive.Ingredient",  # 引用 additive app 的 Ingredient model
        on_delete=models.CASCADE,
        related_name="catfoods",
    )
    # 可选：添加含量字段
    amount = models.CharField(max_length=100, blank=True, help_text="含量说明")
    order = models.IntegerField(default=0, help_text="排序（成分表中的顺序）")

    class Meta:
        db_table = "catfood_ingredient"
        unique_together = [["catfood", "ingredient"]]
        ordering = ["order"]
        verbose_name = "猫粮营养成分"
        verbose_name_plural = "猫粮营养成分"

    def __str__(self):
        return f"{self.catfood.name} - {self.ingredient.name}"


class CatFoodAdditive(models.Model):
    """
    猫粮添加剂关系表
    关联猫粮和添加剂（Additive）
    """

    catfood = models.ForeignKey(
        CatFood,
        on_delete=models.CASCADE,
        related_name="additives",
    )
    additive = models.ForeignKey(
        "additive.Additive",  # 引用 additive app 的 Additive model
        on_delete=models.CASCADE,
        related_name="catfoods",
    )
    amount = models.CharField(max_length=100, blank=True, help_text="添加量说明")
    order = models.IntegerField(default=0, help_text="排序")

    class Meta:
        db_table = "catfood_additive"
        unique_together = [["catfood", "additive"]]
        ordering = ["order"]
        verbose_name = "猫粮添加剂"
        verbose_name_plural = "猫粮添加剂"

    def __str__(self):
        return f"{self.catfood.name} - {self.additive.name}"


class CatFoodRating(models.Model):
    """
    猫粮评分记录
    记录用户对猫粮的评分
    """

    catfood = models.ForeignKey(
        CatFood,
        on_delete=models.CASCADE,
        related_name="ratings",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="catfood_ratings",
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="评分（1-5分）",
    )
    comment = models.TextField(blank=True, help_text="评价内容")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "catfood_rating"
        unique_together = [["catfood", "user"]]  # 一个用户只能评分一次
        verbose_name = "猫粮评分"
        verbose_name_plural = "猫粮评分"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} rated {self.catfood.name}: {self.score}⭐"
