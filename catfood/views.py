"""
猫粮相关视图
"""

from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from comment.models import Comment
from comment.serializers import CommentSerializer

from .models import CatFood
from .serializers import CatFoodCreateUpdateSerializer, CatFoodSerializer


class CatFoodViewSet(viewsets.ModelViewSet):
    """
    猫粮视图集
    提供 CRUD 操作
    """

    queryset = CatFood.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        """根据操作类型返回不同的序列化器"""
        if self.action in ["create", "update", "partial_update"]:
            return CatFoodCreateUpdateSerializer
        return CatFoodSerializer

    def list(self, request, *args, **kwargs):
        """
        获取猫粮列表
        支持分页和排序
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """获取单个猫粮详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """创建新猫粮"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # 使用详情序列化器返回完整数据
        response_serializer = CatFoodSerializer(serializer.instance)
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """更新猫粮（完整更新）"""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # 使用详情序列化器返回完整数据
        response_serializer = CatFoodSerializer(serializer.instance)
        return Response(response_serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """更新猫粮（部分更新）"""
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """删除猫粮"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="search")
    def search_by_name(self, request):
        """
        根据名称搜索猫粮
        GET /api/catfood/search/?name=xxx
        """
        name = request.query_params.get("name", "")

        if not name:
            return Response({"error": "请提供搜索关键词"}, status=status.HTTP_400_BAD_REQUEST)

        # 使用 Q 对象进行模糊搜索（搜索名称和品牌）
        queryset = self.get_queryset().filter(Q(name__icontains=name) | Q(brand__icontains=name))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="comments")
    def get_comments(self, request, pk=None):
        """
        获取某个猫粮的所有评论
        GET /api/catfood/{id}/comments/
        """
        catfood = self.get_object()

        # 查询该猫粮的所有评论
        comments = Comment.objects.filter(target_type="catfood", target_id=catfood.id).order_by(
            "-created_at"
        )

        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = CommentSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = CommentSerializer(comments, many=True, context={"request": request})
        return Response(serializer.data)
