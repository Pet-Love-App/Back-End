"""
评论系统序列化器
"""

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Comment, CommentLike


class CommentAuthorSerializer(serializers.ModelSerializer):
    """评论作者信息序列化器"""

    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "avatar"]

    def get_avatar(self, obj):
        """获取用户头像"""
        try:
            # 假设用户模型有 profile 关联（需要根据实际情况调整）
            if hasattr(obj, "profile") and obj.profile.avatar:
                return obj.profile.avatar.url
        except Exception:
            # 捕获任何异常并忽略
            pass
        return None


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""

    author = CommentAuthorSerializer(read_only=True)
    isLiked = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "content",
            "author",
            "createdAt",
            "likes",
            "isLiked",
            "target_type",
            "target_id",
        ]
        read_only_fields = ["id", "author", "likes", "createdAt"]

    def get_isLiked(self, obj):
        """检查当前用户是否已点赞"""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return CommentLike.objects.filter(comment=obj, user=request.user).exists()
        return False


class CommentCreateSerializer(serializers.ModelSerializer):
    """创建评论序列化器"""

    targetId = serializers.IntegerField(source="target_id")
    targetType = serializers.ChoiceField(
        source="target_type", choices=["post", "catfood", "report"]
    )

    class Meta:
        model = Comment
        fields = ["content", "targetId", "targetType"]

    def create(self, validated_data):
        """创建评论，自动设置作者为当前用户"""
        request = self.context.get("request")
        validated_data["author"] = request.user
        return super().create(validated_data)


class CommentLikeSerializer(serializers.Serializer):
    """评论点赞序列化器"""

    comment_id = serializers.IntegerField()

    def validate_comment_id(self, value):
        """验证评论是否存在"""
        try:
            Comment.objects.get(id=value)
        except Comment.DoesNotExist as e:
            raise serializers.ValidationError("评论不存在") from e
        return value

    def create(self, validated_data):
        """创建或删除点赞记录"""
        request = self.context.get("request")
        comment_id = validated_data["comment_id"]
        comment = Comment.objects.get(id=comment_id)
        user = request.user

        # 检查是否已点赞
        like_record = CommentLike.objects.filter(comment=comment, user=user).first()

        if like_record:
            # 如果已点赞，则取消点赞
            like_record.delete()
            comment.likes = max(0, comment.likes - 1)
            comment.save()
            return {"action": "unliked", "likes": comment.likes}
        else:
            # 如果未点赞，则添加点赞
            CommentLike.objects.create(comment=comment, user=user)
            comment.likes += 1
            comment.save()
            return {"action": "liked", "likes": comment.likes}
