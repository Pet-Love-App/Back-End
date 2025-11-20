"""
评论系统序列化器 + 帖子/通知
"""

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Comment, CommentLike, Post, PostMedia, Favorite, Notification


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


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
    targetType = serializers.ChoiceField(source="target_type", choices=["post", "catfood", "report"], required=True)
    parentId = serializers.IntegerField(source="parent.id", required=False, allow_null=True)

    class Meta:
        model = Comment
        fields = ["content", "targetId", "targetType", "parentId"]

    def validate(self, data):
        target_type = data.get("target_type")
        target_id = data.get("target_id")
        if target_type == "catfood":
            from catfood.models import CatFood
            if not CatFood.objects.filter(id=target_id).exists():
                raise serializers.ValidationError({"targetId": f"ID为{target_id}的猫粮不存在"})
        elif target_type == "post":
            if not Post.objects.filter(id=target_id).exists():
                raise serializers.ValidationError({"targetId": f"ID为{target_id}的帖子不存在"})
        elif target_type == "report":
            from ai_report.models import Report
            if not Report.objects.filter(id=target_id).exists():
                raise serializers.ValidationError({"targetId": f"ID为{target_id}的报告不存在"})
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
        return super().create(validated_data)


class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["content"]


class CommentLikeSerializer(serializers.Serializer):
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
            like_record.delete()
            comment.likes = max(0, comment.likes - 1)
            comment.save(update_fields=["likes"])
            return {"action": "unliked", "likes": comment.likes}
        else:
            CommentLike.objects.create(comment=comment, user=user)
            comment.likes += 1
            comment.save(update_fields=["likes"])
            return {"action": "liked", "likes": comment.likes}


class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ["id", "media_type", "file", "created_at"]
        read_only_fields = ["id", "media_type", "created_at"]


class PostSerializer(serializers.ModelSerializer):
    media = PostMediaSerializer(many=True, read_only=True)
    favorites_count = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    author = UserSimpleSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ["id", "author", "content", "media", "favorites_count", "is_favorited", "created_at", "updated_at"]
        read_only_fields = ["id", "author", "favorites_count", "is_favorited", "created_at", "updated_at"]

    def get_favorites_count(self, obj):
        return obj.favorites.count()

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.favorites.filter(user=request.user).exists()
        return False


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["content"]

    def create(self, validated_data):
        request = self.context.get("request")
        post = Post.objects.create(author=request.user, **validated_data)
        files = request.FILES.getlist("media")
        for f in files:
            ct = getattr(f, "content_type", "") or ""
            media_type = PostMedia.IMAGE if ct.startswith("image/") else PostMedia.VIDEO
            PostMedia.objects.create(post=post, file=f, media_type=media_type)
        return post


class FavoriteToggleSerializer(serializers.Serializer):
    post_id = serializers.IntegerField()

    def validate_post_id(self, value):
        if not Post.objects.filter(id=value).exists():
            raise serializers.ValidationError("帖子不存在")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        post = Post.objects.get(id=validated_data["post_id"])
        fav = Favorite.objects.filter(user=request.user, post=post).first()
        if fav:
            fav.delete()
            return {"action": "unfavorited", "favorites_count": post.favorites.count()}
        Favorite.objects.create(user=request.user, post=post)
        return {"action": "favorited", "favorites_count": post.favorites.count()}


class NotificationSerializer(serializers.ModelSerializer):
    actor = UserSimpleSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "actor", "verb", "post", "comment", "unread", "created_at"]
        read_only_fields = fields
