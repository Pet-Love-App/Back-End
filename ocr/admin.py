from django.contrib import admin
from .models import OcrResult

@admin.register(OcrResult)
class OcrResultAdmin(admin.ModelAdmin):
    list_display = ("id", "image_thumbnail", "created_at", "confidence", "text_preview")
    search_fields = ("recognized_text",)
    list_filter = ("created_at",)
    readonly_fields = ("image_preview",)  # 详情页显示大图

    def image_thumbnail(self, obj):
        """列表页显示缩略图"""
        if obj.image_url:
            return f'<img src="{obj.image_url}" style="width: 100px; height: auto;" />'
        return "无图片"
    image_thumbnail.allow_tags = True
    image_thumbnail.short_description = "图片预览"

    def text_preview(self, obj):
        """列表页显示文本预览"""
        return obj.recognized_text[:50] + "..." if len(obj.recognized_text) > 50 else obj.recognized_text
    text_preview.short_description = "识别文本预览"

    def image_preview(self, obj):
        """详情页显示大图"""
        if obj.image_url:
            return f'<img src="{obj.image_url}" style="max-width: 500px;" />'
        return "无图片"
    image_preview.allow_tags = True