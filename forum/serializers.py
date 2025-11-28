"""
论坛系统序列化器
包含帖子、收藏、通知相关序列化器
"""

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Favorite, Notification, Post, PostMedia


class UserSimpleSerializer(serializers.ModelSerializer):
    """
    简单用户信息序列化器
    用于在帖子和通知中显示用户基本信息
    """

    class Meta:
        model = User
        fields = ["id", "username"]
        read_only_fields = fields


class PostMediaSerializer(serializers.ModelSerializer):
    """
    帖子媒体序列化器
    处理帖子中的图片和视频
    """

    file_url = serializers.SerializerMethodField()

    class Meta:
        model = PostMedia
        fields = ["id", "media_type", "file", "file_url", "created_at"]
        read_only_fields = ["id", "media_type", "file_url", "created_at"]

    def get_file_url(self, obj):
        """返回完整的文件 URL"""
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url if obj.file else None


class PostSerializer(serializers.ModelSerializer):
    """
    帖子序列化器
    用于列表和详情展示
    """

    author = UserSimpleSerializer(read_only=True)
    media = PostMediaSerializer(many=True, read_only=True)
    favorites_count = serializers.IntegerField(read_only=True, source="favorites.count")
    is_favorited = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "content",
            "media",
            "favorites_count",
            "is_favorited",
            "comments_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_is_favorited(self, obj):
        """判断当前用户是否已收藏"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_comments_count(self, obj):
        """获取评论数量"""
        from comment.models import Comment

        return Comment.objects.filter(target_type="post", target_id=obj.id).count()


class PostCreateSerializer(serializers.ModelSerializer):
    """
    创建帖子序列化器
    支持上传多个媒体文件（图片/视频）
    """

    class Meta:
        model = Post
        fields = ["content"]

    def validate_content(self, value):
        """验证帖子内容"""
        if not value or not value.strip():
            raise serializers.ValidationError("帖子内容不能为空")
        if len(value) > 5000:
            raise serializers.ValidationError("帖子内容不能超过 5000 字")
        return value.strip()

    def create(self, validated_data):
        """
        创建帖子并处理媒体文件
        作者在 view 层已设置
        """
        request = self.context.get("request")
        post = Post.objects.create(**validated_data)

        # 处理上传的媒体文件
        media_files = request.FILES.getlist("media")
        if len(media_files) > 9:
            raise serializers.ValidationError({"media": "最多只能上传 9 个媒体文件"})

        for media_file in media_files:
            # 验证文件大小（10MB）
            if media_file.size > 10 * 1024 * 1024:
                raise serializers.ValidationError({"media": "单个文件大小不能超过 10MB"})

            # 根据 content_type 判断媒体类型
            content_type = getattr(media_file, "content_type", "") or ""
            if content_type.startswith("image/"):
                media_type = PostMedia.IMAGE
            elif content_type.startswith("video/"):
                media_type = PostMedia.VIDEO
            else:
                continue  # 跳过不支持的文件类型

            PostMedia.objects.create(post=post, file=media_file, media_type=media_type)

        return post


class FavoriteToggleSerializer(serializers.Serializer):
    """
    收藏切换序列化器
    用于收藏/取消收藏帖子
    """

    post_id = serializers.IntegerField(required=True)

    def validate_post_id(self, value):
        """验证帖子是否存在"""
        try:
            Post.objects.get(id=value)
        except Post.DoesNotExist as e:
            raise serializers.ValidationError("帖子不存在") from e
        return value

    def create(self, validated_data):
        """切换收藏状态"""
        request = self.context.get("request")
        post = Post.objects.get(id=validated_data["post_id"])
        user = request.user

        # 查询是否已收藏
        favorite = Favorite.objects.filter(user=user, post=post).first()

        if favorite:
            # 已收藏，取消收藏
            favorite.delete()
            action = "unfavorited"
        else:
            # 未收藏，添加收藏
            Favorite.objects.create(user=user, post=post)
            action = "favorited"

        return {
            "action": action,
            "is_favorited": action == "favorited",
            "favorites_count": post.favorites.count(),
        }


class NotificationSerializer(serializers.ModelSerializer):
    """
    通知序列化器
    用于展示用户通知
    """

    actor = UserSimpleSerializer(read_only=True)
    verb_display = serializers.SerializerMethodField()
    post_id = serializers.IntegerField(source="post.id", read_only=True)
    comment_id = serializers.IntegerField(source="comment.id", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "actor",
            "verb",
            "verb_display",
            "post_id",
            "comment_id",
            "unread",
            "created_at",
        ]
        read_only_fields = fields

    def get_verb_display(self, obj):
        """返回动作的中文描述"""
        verb_map = {
            "comment_post": "评论了你的帖子",
            "reply_comment": "回复了你的评论",
        }
        return verb_map.get(obj.verb, obj.verb)
