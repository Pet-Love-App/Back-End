"""
用户序列化器
"""

from django.contrib.auth.models import User
from rest_framework import serializers
from reputation.serializers import ReputationSummarySerializer, UserBadgeSerializer
from reputation.models import UserBadge

from .models import Pet, UserProfile


class PetSerializer(serializers.ModelSerializer):
    """宠物序列化器"""

    species_display = serializers.CharField(source="get_species_display", read_only=True)

    class Meta:
        model = Pet
        fields = [
            "id",
            "name",
            "species",
            "species_display",
            "breed",
            "age",
            "photo",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserProfileSerializer(serializers.ModelSerializer):
    """用户资料序列化器"""

    class Meta:
        model = UserProfile
        fields = ["avatar", "bio", "phone", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器 - 完整的用户信息（包含头像和宠物）"""

    avatar = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    pets = PetSerializer(many=True, read_only=True)
    reputation = ReputationSummarySerializer(read_only=True)
    badges = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ["id", "username", "avatar", "pets","reputation", "badges", "is_admin"]
        read_only_fields = ["id"]

    def get_avatar(self, obj):
        """获取用户头像 URL"""
        try:
            if obj.profile and obj.profile.avatar:
                request = self.context.get("request")
                if request:
                    return request.build_absolute_uri(obj.profile.avatar.url)
                return obj.profile.avatar.url
        except UserProfile.DoesNotExist:
            pass
        return None
    
    def get_badges(self, obj):
        badges = UserBadge.objects.filter(user=obj).select_related("badge").order_by("-is_equipped", "-acquired_at")
        from reputation.serializers import UserBadgeSerializer
        return UserBadgeSerializer(badges, many=True).data

    def get_is_admin(self, obj):
        """获取用户管理员状态"""
        try:
            return obj.profile.is_admin if obj.profile else False
        except UserProfile.DoesNotExist:
            return False


class AvatarUploadSerializer(serializers.Serializer):
    """头像上传序列化器"""

    avatar = serializers.ImageField(required=True)

    def validate_avatar(self, value):
        """验证头像文件"""
        # 验证文件大小 (5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("图片大小不能超过 5MB")

        # 验证文件类型
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
        if value.content_type not in allowed_types:
            raise serializers.ValidationError("只支持 JPG, PNG, WEBP 格式")

        return value
