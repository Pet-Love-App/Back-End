from django.contrib import admin

from additive.models import Additive, Ingredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """营养成分管理"""

    list_display = ["id", "name", "type", "label"]
    list_filter = ["type", "label"]
    search_fields = ["name", "type", "desc"]
    ordering = ["name"]


@admin.register(Additive)
class AdditiveAdmin(admin.ModelAdmin):
    """添加剂管理"""

    list_display = ["id", "name", "en_name", "type", "applicable_range"]
    list_filter = ["type", "applicable_range"]
    search_fields = ["name", "en_name", "type"]
    ordering = ["name"]
