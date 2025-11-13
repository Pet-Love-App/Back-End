from django.contrib import admin

from .models import Comment, CommentLike


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """评论管理"""

    list_display = [
        "id",
        "author",
        "content_preview",
        "target_type",
        "target_id",
        "likes",
        "created_at",
    ]
    list_filter = ["target_type", "created_at"]
    search_fields = ["content", "author__username"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"

    def content_preview(self, obj):
        """显示评论预览"""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "内容预览"


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    """评论点赞管理"""

    list_display = ["id", "comment", "user", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__username", "comment__content"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"
