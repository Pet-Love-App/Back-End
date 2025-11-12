"""
评论相关视图
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Comment
from .serializers import (
    CommentCreateSerializer,
    CommentLikeSerializer,
    CommentSerializer,
    CommentUpdateSerializer,
)


class CommentViewSet(viewsets.ModelViewSet):
    """
    评论视图集
    提供评论的 CRUD 操作
    """

    queryset = Comment.objects.all().order_by("-created_at")
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """根据操作类型返回不同的序列化器"""
        if self.action == "create":
            return CommentCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return CommentUpdateSerializer
        return CommentSerializer

    def get_permissions(self):
        """
        根据操作类型设置权限
        - 创建评论需要登录
        - 列表和详情可以匿名访问
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
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

        # 使用详情序列化器返回完整数据
        response_serializer = CommentSerializer(serializer.instance, context={"request": request})
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
        serializer = CommentLikeSerializer(
            data={"comment_id": comment.id}, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        # 返回更新后的评论信息
        comment.refresh_from_db()
        response_serializer = CommentSerializer(comment, context={"request": request})

        return Response(
            {
                "action": result["action"],
                "likes": result["likes"],
                "comment": response_serializer.data,
            },
            status=status.HTTP_200_OK,
        )
