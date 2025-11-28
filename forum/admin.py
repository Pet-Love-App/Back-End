"""
论坛系统管理后台
"""

from django.contrib import admin

from .models import Favorite, Notification, Post, PostMedia


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """帖子管理"""

    list_display = ["id", "author", "content_preview", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["content", "author__username"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"

    def content_preview(self, obj):
        """显示内容预览"""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "内容预览"


@admin.register(PostMedia)
class PostMediaAdmin(admin.ModelAdmin):
    """帖子媒体管理"""

    list_display = ["id", "post", "media_type", "created_at"]
    list_filter = ["media_type", "created_at"]
    search_fields = ["post__content"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """收藏管理"""

    list_display = ["id", "user", "post", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__username", "post__content"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """通知管理"""

    list_display = ["id", "recipient", "actor", "verb", "unread", "created_at"]
    list_filter = ["verb", "unread", "created_at"]
    search_fields = ["recipient__username", "actor__username"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"
