"""
评论相关视图 + 帖子/通知/收藏/消息
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import F
from django.db.models.functions import Random

from .models import Comment, Post, Favorite, Notification
from .serializers import (
    CommentCreateSerializer,
    CommentLikeSerializer,
    CommentSerializer,
    CommentUpdateSerializer,
    PostSerializer,
    PostCreateSerializer,
    FavoriteToggleSerializer,
    NotificationSerializer,
)


class CommentViewSet(viewsets.ModelViewSet):
    """
    评论视图集
    提供评论的 CRUD 操作 + 点赞 + 按赞数排序 + 回复
    """

    queryset = Comment.objects.all().order_by("-created_at")
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == "create":
            return CommentCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return CommentUpdateSerializer
        return CommentSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "like"]:
            return [IsAuthenticated()]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        """
        获取评论列表
        支持按 target_type 和 target_id 过滤
        """
        queryset = self.filter_queryset(self.get_queryset())

        # 过滤条件
        target_type = request.query_params.get("target_type")
        target_id = request.query_params.get("target_id")

        if target_type:
            queryset = queryset.filter(target_type=target_type)
        if target_id:
            queryset = queryset.filter(target_id=target_id)

        # 排序
        order_by = request.query_params.get("order_by")
        if order_by == "likes":
            queryset = queryset.order_by("-likes", "-created_at")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """创建新评论"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        response_serializer = CommentSerializer(serializer.instance, context={"request": request})

        # 仅论坛发帖触发通知（target_type == "post"），其它类型不触发
        try:
            comment_obj = serializer.instance
            if comment_obj.target_type == "post":
                post = Post.objects.filter(id=comment_obj.target_id).first()
                # 通知帖子作者（排除自己）
                if post and post.author != request.user:
                    Notification.objects.create(
                        recipient=post.author,
                        actor=request.user,
                        verb="comment_post" if not comment_obj.parent else "reply_comment",
                        post=post,
                        comment=comment_obj,
                    )
                # 回复评论 -> 通知父评论作者（排除自己）
                if comment_obj.parent and comment_obj.parent.author != request.user:
                    Notification.objects.create(
                        recipient=comment_obj.parent.author,
                        actor=request.user,
                        verb="reply_comment",
                        post=post,
                        comment=comment_obj,
                    )
        except Exception:
            pass

        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """更新评论（仅作者可更新）"""
        instance = self.get_object()

        # 检查是否是评论作者
        if instance.author != request.user:
            return Response({"error": "您没有权限修改此评论"}, status=status.HTTP_403_FORBIDDEN)

        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        response_serializer = CommentSerializer(serializer.instance, context={"request": request})
        return Response(response_serializer.data)

    def destroy(self, request, *args, **kwargs):
        """删除评论（仅作者可删除）"""
        instance = self.get_object()

        # 检查是否是评论作者
        if instance.author != request.user:
            return Response({"error": "您没有权限删除此评论"}, status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """
        点赞/取消点赞评论
        POST /api/comments/{id}/like/
        """
        comment = self.get_object()

        # 使用序列化器处理点赞逻辑
        serializer = CommentLikeSerializer(data={"comment_id": comment.id}, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        # 返回更新后的评论信息
        comment.refresh_from_db()
        response_serializer = CommentSerializer(comment, context={"request": request})

        return Response(
            {"action": result["action"], "likes": result["likes"], "comment": response_serializer.data},
            status=status.HTTP_200_OK,
        )


class PostViewSet(viewsets.ModelViewSet):
    """帖子视图：广场随机 / 最新、创建、收藏列表、收藏切换"""
    queryset = Post.objects.all().order_by("-created_at").select_related("author")
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == "create":
            return PostCreateSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save()

    def list(self, request, *args, **kwargs):
        order = request.query_params.get("order")  # random | latest
        qs = self.get_queryset()
        if order == "random":
            qs = qs.order_by(Random())
        else:
            qs = qs.order_by("-created_at")
        page = self.paginate_queryset(qs)
        if page is not None:
            ser = PostSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(ser.data)
        ser = PostSerializer(qs, many=True, context={"request": request})
        return Response(ser.data)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def favorites(self, request):
        qs = Post.objects.filter(favorites__user=request.user).order_by("-favorites__created_at")
        page = self.paginate_queryset(qs)
        if page is not None:
            ser = PostSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(ser.data)
        ser = PostSerializer(qs, many=True, context={"request": request})
        return Response(ser.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        post = self.get_object()
        serializer = FavoriteToggleSerializer(data={"post_id": post.id}, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_200_OK)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """消息视图：获取未读/全部、标记已读、全部设为已读"""
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        qs = Notification.objects.filter(recipient=self.request.user).order_by("-created_at")
        unread = self.request.query_params.get("unread")
        if unread == "true":
            qs = qs.filter(unread=True)
        return qs

    @action(detail=True, methods=["post"])
    def read(self, request, pk=None):
        n = self.get_object()
        if n.recipient != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if n.unread:
            n.unread = False
            n.save(update_fields=["unread"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"])
    def read_all(self, request):
        Notification.objects.filter(recipient=request.user, unread=True).update(unread=False)
        return Response(status=status.HTTP_204_NO_CONTENT)
