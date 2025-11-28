"""
论坛系统视图
包含帖子、通知相关视图
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Notification, Post
from .serializers import (
    FavoriteToggleSerializer,
    NotificationSerializer,
    PostCreateSerializer,
    PostSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    """
    帖子视图集
    提供帖子的 CRUD 操作 + 收藏功能
    """

    queryset = Post.objects.all().select_related("author").prefetch_related("media", "favorites")
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ["get", "post", "delete"]  # 只允许这些方法

    def get_queryset(self):
        """优化查询，按创建时间倒序"""
        return super().get_queryset().order_by("-created_at")

    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == "create":
            return PostCreateSerializer
        return PostSerializer

    def perform_create(self, serializer):
        """创建帖子时自动设置作者"""
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """
        删除帖子
        仅作者可删除自己的帖子
        """
        post = self.get_object()

        if post.author != request.user:
            return Response({"detail": "您没有权限删除此帖子"}, status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(post)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def favorites(self, request):
        """
        获取我的收藏列表
        GET /api/forum/posts/favorites/
        返回当前用户收藏的所有帖子，按收藏时间倒序
        """
        queryset = (
            Post.objects.filter(favorites__user=request.user)
            .select_related("author")
            .prefetch_related("media", "favorites")
            .order_by("-favorites__created_at")
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """
        收藏/取消收藏帖子
        POST /api/forum/posts/{id}/favorite/
        切换收藏状态
        """
        post = self.get_object()
        serializer = FavoriteToggleSerializer(
            data={"post_id": post.id}, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_200_OK)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    通知视图集
    提供通知的查看、标记已读功能
    """

    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        """
        获取当前用户的通知
        支持过滤：unread=true(仅未读)
        优化查询性能，使用 select_related
        """
        queryset = (
            Notification.objects.filter(recipient=self.request.user)
            .select_related("actor", "post", "comment")
            .order_by("-created_at")
        )

        # 过滤未读通知
        unread_only = self.request.query_params.get("unread")
        if unread_only == "true":
            queryset = queryset.filter(unread=True)

        return queryset

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """
        标记单条通知为已读
        POST /api/forum/notifications/{id}/mark_read/
        """
        notification = self.get_object()

        # 验证权限
        if notification.recipient != request.user:
            return Response({"detail": "无权操作此通知"}, status=status.HTTP_403_FORBIDDEN)

        # 标记为已读
        if notification.unread:
            notification.unread = False
            notification.save(update_fields=["unread"])

        return Response({"detail": "已标记为已读"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """
        标记所有通知为已读
        POST /api/forum/notifications/mark_all_read/
        """
        updated_count = Notification.objects.filter(recipient=request.user, unread=True).update(
            unread=False
        )

        return Response(
            {"detail": f"已标记 {updated_count} 条通知为已读"}, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        """
        获取未读通知数量
        GET /api/forum/notifications/unread_count/
        """
        count = Notification.objects.filter(recipient=request.user, unread=True).count()

        return Response({"count": count}, status=status.HTTP_200_OK)
