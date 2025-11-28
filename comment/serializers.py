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
            if hasattr(obj, "profile") and obj.profile.avatar:
                return obj.profile.avatar.url
        except Exception:
            pass
        return None


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""

    author = CommentAuthorSerializer(read_only=True)
    isLiked = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    replies = serializers.SerializerMethodField()
    parent_id = serializers.IntegerField(source="parent.id", read_only=True)

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
            "parent_id",
            "replies",
        ]
        read_only_fields = ["id", "author", "likes", "createdAt", "parent_id", "replies"]

    def get_isLiked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return CommentLike.objects.filter(comment=obj, user=request.user).exists()
        return False

    def get_replies(self, obj):
        # 只在请求参数 include_replies=true 时返回（避免性能问题）
        request = self.context.get("request")
        if request and request.query_params.get("include_replies") == "true":
            qs = obj.replies.all().order_by("-likes", "-created_at")
            return CommentSerializer(qs, many=True, context=self.context).data
        return []


class CommentCreateSerializer(serializers.ModelSerializer):
    """创建评论序列化器"""

    targetId = serializers.IntegerField(source="target_id", required=True)
    targetType = serializers.ChoiceField(
        source="target_type", choices=["post", "catfood", "report"], required=True
    )
    parentId = serializers.IntegerField(source="parent.id", required=False, allow_null=True)

    class Meta:
        model = Comment
        fields = ["content", "targetId", "targetType", "parentId"]

    def validate(self, data):
        target_type = data.get("target_type")
        target_id = data.get("target_id")

        # 验证目标对象是否存在
        if target_type == "catfood":
            from catfood.models import CatFood

            if not CatFood.objects.filter(id=target_id).exists():
                raise serializers.ValidationError({"targetId": f"ID为{target_id}的猫粮不存在"})
        elif target_type == "post":
            from forum.models import Post

            if not Post.objects.filter(id=target_id).exists():
                raise serializers.ValidationError({"targetId": f"ID为{target_id}的帖子不存在"})
        elif target_type == "report":
            from ai_report.models import Report

            if not Report.objects.filter(id=target_id).exists():
                raise serializers.ValidationError({"targetId": f"ID为{target_id}的报告不存在"})

        # 验证父评论是否存在
        parent_id = self.initial_data.get("parentId")
        if parent_id:
            try:
                parent_obj = Comment.objects.get(id=parent_id)
                data["parent"] = parent_obj
            except Comment.DoesNotExist:
                raise serializers.ValidationError({"parentId": "父评论不存在"})

        return data

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["author"] = request.user
        comment = super().create(validated_data)

        # 如果是对帖子的评论，触发通知
        if comment.target_type == "post":
            self._create_post_notification(comment, request.user)

        return comment

    def _create_post_notification(self, comment, user):
        """为帖子评论创建通知"""
        try:
            from forum.models import Notification, Post

            post = Post.objects.filter(id=comment.target_id).first()

            if not post:
                return

            # 通知帖子作者（排除自己）
            if post.author != user:
                Notification.objects.create(
                    recipient=post.author,
                    actor=user,
                    verb="comment_post" if not comment.parent else "reply_comment",
                    post=post,
                    comment=comment,
                )

            # 回复评论 -> 通知父评论作者（排除自己）
            if comment.parent and comment.parent.author != user:
                Notification.objects.create(
                    recipient=comment.parent.author,
                    actor=user,
                    verb="reply_comment",
                    post=post,
                    comment=comment,
                )
        except Exception:
            pass


class CommentUpdateSerializer(serializers.ModelSerializer):
    """更新评论序列化器"""

    class Meta:
        model = Comment
        fields = ["content"]


class CommentLikeSerializer(serializers.Serializer):
    """评论点赞序列化器"""

    comment_id = serializers.IntegerField()

    def validate_comment_id(self, value):
        try:
            Comment.objects.get(id=value)
        except Comment.DoesNotExist as e:
            raise serializers.ValidationError("评论不存在") from e
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        comment_id = validated_data["comment_id"]
        comment = Comment.objects.get(id=comment_id)
        user = request.user

        like_record = CommentLike.objects.filter(comment=comment, user=user).first()
        if like_record:
            # 取消点赞
            like_record.delete()
            comment.likes = max(0, comment.likes - 1)
            comment.save(update_fields=["likes"])
            return {"action": "unliked", "likes": comment.likes}
        else:
            # 点赞
            CommentLike.objects.create(comment=comment, user=user)
            comment.likes += 1
            comment.save(update_fields=["likes"])
            return {"action": "liked", "likes": comment.likes}
