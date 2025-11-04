"""
用户相关模型
"""

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image


def user_avatar_path(instance, filename):
    """生成头像保存路径"""
    ext = filename.split(".")[-1]
    return f"avatars/user_{instance.user.id}/avatar.{ext}"


class UserProfile(models.Model):
    """用户资料扩展 - 存储头像等扩展信息"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        blank=True,
        null=True,
        help_text="用户头像",
    )
    bio = models.TextField(max_length=500, blank=True, help_text="个人简介")
    phone = models.CharField(max_length=20, blank=True, help_text="手机号")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_profile"
        verbose_name = "用户资料"
        verbose_name_plural = "用户资料"

    def __str__(self):
        return f"{self.user.username} Profile"

    def save(self, *args, **kwargs):
        """保存时自动压缩头像"""
        super().save(*args, **kwargs)

        if self.avatar:
            try:
                img = Image.open(self.avatar.path)

                # 转换 RGBA 为 RGB（处理 PNG 透明度）
                if img.mode in ("RGBA", "LA", "P"):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                    img = background

                # 压缩大图到 400x400
                if img.height > 400 or img.width > 400:
                    output_size = (400, 400)
                    img.thumbnail(output_size, Image.Resampling.LANCZOS)

                # 保存优化后的图片
                img.save(self.avatar.path, quality=85, optimize=True)
            except Exception as e:
                print(f"头像压缩失败: {e}")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """用户创建时自动创建 profile"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """用户保存时同步保存 profile"""
    if hasattr(instance, "profile"):
        instance.profile.save()


class Pet(models.Model):
    """宠物模型"""

    SPECIES_CHOICES = [
        ("dog", "狗"),
        ("cat", "猫"),
        ("bird", "鸟"),
        ("fish", "鱼"),
        ("rabbit", "兔子"),
        ("hamster", "仓鼠"),
        ("other", "其他"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pets")
    name = models.CharField(max_length=50, help_text="宠物名字")
    species = models.CharField(
        max_length=30, choices=SPECIES_CHOICES, default="dog", help_text="物种"
    )
    breed = models.CharField(max_length=50, blank=True, help_text="品种")
    age = models.IntegerField(null=True, blank=True, help_text="年龄")
    photo = models.ImageField(upload_to="pets/", blank=True, null=True, help_text="宠物照片")
    description = models.TextField(max_length=200, blank=True, help_text="描述")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pet"
        verbose_name = "宠物"
        verbose_name_plural = "宠物"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_species_display()})"
