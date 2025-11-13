"""
用户模块后台管理
"""

from django.contrib import admin

from .models import Pet, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """用户资料后台管理"""

    list_display = ["user", "phone", "created_at", "updated_at"]
    search_fields = ["user__username", "user__email", "phone"]
    list_filter = ["created_at"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    """宠物后台管理"""

    list_display = ["name", "species", "breed", "age", "user", "created_at"]
    search_fields = ["name", "breed", "user__username"]
    list_filter = ["species", "created_at"]
    readonly_fields = ["created_at", "updated_at"]
