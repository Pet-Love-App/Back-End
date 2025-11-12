from django.contrib import admin

from .models import (
    CatFood,
    CatFoodAdditive,
    CatFoodFavorite,
    CatFoodIngredient,
    CatFoodRating,
    CatFoodTag,
    CatFoodTagRelation,
)


class CatFoodIngredientInline(admin.TabularInline):
    """猫粮营养成分内联编辑"""

    model = CatFoodIngredient
    extra = 1
    autocomplete_fields = ["ingredient"]


class CatFoodAdditiveInline(admin.TabularInline):
    """猫粮添加剂内联编辑"""

    model = CatFoodAdditive
    extra = 1
    autocomplete_fields = ["additive"]


class CatFoodTagRelationInline(admin.TabularInline):
    """猫粮标签内联编辑"""

    model = CatFoodTagRelation
    extra = 1
    autocomplete_fields = ["tag"]


@admin.register(CatFood)
class CatFoodAdmin(admin.ModelAdmin):
    """猫粮管理"""

    list_display = [
        "id",
        "name",
        "brand",
        "score",
        "count_num",
        "percentage",
        "created_at",
    ]
    list_filter = ["brand", "percentage", "created_at"]
    search_fields = ["name", "brand", "desc"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("基本信息", {"fields": ("name", "brand", "desc", "image_url")}),
        (
            "评分信息",
            {
                "fields": ("score", "count_num"),
            },
        ),
        (
            "营养成分分析",
            {
                "fields": (
                    "percentage",
                    "crude_protein",
                    "crude_fat",
                    "carbohydrates",
                    "crude_fiber",
                    "crude_ash",
                    "others",
                ),
            },
        ),
        (
            "分析内容",
            {
                "fields": ("safety", "nutrient"),
            },
        ),
        (
            "时间信息",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )

    inlines = [CatFoodTagRelationInline, CatFoodIngredientInline, CatFoodAdditiveInline]


@admin.register(CatFoodTag)
class CatFoodTagAdmin(admin.ModelAdmin):
    """猫粮标签管理"""

    list_display = ["id", "name", "created_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at"]


@admin.register(CatFoodRating)
class CatFoodRatingAdmin(admin.ModelAdmin):
    """猫粮评分管理"""

    list_display = ["id", "catfood", "user", "score", "created_at"]
    list_filter = ["score", "created_at"]
    search_fields = ["catfood__name", "user__username", "comment"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"


@admin.register(CatFoodIngredient)
class CatFoodIngredientAdmin(admin.ModelAdmin):
    """猫粮营养成分关系管理"""

    list_display = ["id", "catfood", "ingredient", "amount", "order"]
    list_filter = ["catfood"]
    search_fields = ["catfood__name", "ingredient__name"]
    autocomplete_fields = ["catfood", "ingredient"]


@admin.register(CatFoodAdditive)
class CatFoodAdditiveAdmin(admin.ModelAdmin):
    """猫粮添加剂关系管理"""

    list_display = ["id", "catfood", "additive", "amount", "order"]
    list_filter = ["catfood"]
    search_fields = ["catfood__name", "additive__name"]
    autocomplete_fields = ["catfood", "additive"]


@admin.register(CatFoodFavorite)
class CatFoodFavoriteAdmin(admin.ModelAdmin):
    """猫粮收藏管理"""

    list_display = ["id", "user", "catfood", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__username", "catfood__name", "catfood__brand"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"
    autocomplete_fields = ["user", "catfood"]
