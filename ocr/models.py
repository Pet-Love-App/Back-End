from django.db import models
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

class OcrResult(models.Model):
    """OCR识别结果模型（优化版）"""
    # 改用ImageField自动管理文件，支持URL访问
    image = models.ImageField(upload_to='ocr_images/', help_text="上传的图片")
    recognized_text = models.TextField(help_text="识别出的文本")
    created_at = models.DateTimeField(default=timezone.now, help_text="识别时间")
    confidence = models.FloatField(default=0.0, help_text="识别平均置信度")  # 默认为0.0

    class Meta:
        db_table = "ocr_result"
        ordering = ["-created_at"]

    def __str__(self):
        return f"OCR Result: {self.image.name}"

    @property
    def image_url(self):
        """返回图片的URL（便于前端访问）"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None