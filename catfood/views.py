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

from .models import CatFood, CatFoodFavorite
from .serializers import (
    CatFoodCreateUpdateSerializer,
    CatFoodFavoriteSerializer,
    CatFoodSerializer,
)


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

    @action(detail=False, methods=["post"], url_path="scan-barcode")
    def scan_barcode(self, request):
        """
        扫描条形码并返回猫粮信息
        如果条形码不存在，返回404
        POST /api/catfood/scan-barcode/
        Body: {
            "barcode": "6901234567890"
        }
        """
        barcode = request.data.get("barcode")

        if not barcode:
            return Response({"error": "请提供条形码"}, status=status.HTTP_400_BAD_REQUEST)

        # 查找是否已存在该条形码的猫粮
        try:
            catfood = CatFood.objects.get(barcode=barcode)
            serializer = CatFoodSerializer(catfood)
            return Response(
                {
                    "exists": True,
                    "message": "找到已有猫粮",
                    "catfood": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except CatFood.DoesNotExist:
            # 条形码不存在
            return Response(
                {
                    "exists": False,
                    "message": "条形码未注册，数据库中暂无该猫粮信息",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["get"], url_path="by-barcode")
    def get_by_barcode(self, request):
        """
        通过条形码查询猫粮
        GET /api/catfood/by-barcode/?barcode=xxx
        """
        barcode = request.query_params.get("barcode")

        if not barcode:
            return Response({"error": "请提供条形码"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            catfood = CatFood.objects.get(barcode=barcode)
            serializer = CatFoodSerializer(catfood)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CatFood.DoesNotExist:
            return Response(
                {"error": "未找到该条形码对应的猫粮"},
                status=status.HTTP_404_NOT_FOUND,
            )


class CatFoodFavoriteViewSet(viewsets.ModelViewSet):
    """
    猫粮收藏视图集
    """

    serializer_class = CatFoodFavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """只返回当前用户的收藏"""
        return CatFoodFavorite.objects.filter(user=self.request.user).select_related("catfood")

    def list(self, request, *args, **kwargs):
        """
        获取当前用户的收藏列表
        GET /api/catfood/favorites/
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        收藏猫粮
        POST /api/catfood/favorites/
        Body: {"catfood_id": 1}
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        """
        取消收藏
        DELETE /api/catfood/favorites/{id}/
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "取消收藏成功"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="toggle")
    def toggle_favorite(self, request):
        """
        切换收藏状态（收藏/取消收藏）
        POST /api/catfood/favorites/toggle/
        Body: {"catfood_id": 1}
        """
        catfood_id = request.data.get("catfood_id")

        if not catfood_id:
            return Response({"error": "请提供 catfood_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            catfood = CatFood.objects.get(id=catfood_id)
        except CatFood.DoesNotExist:
            return Response({"error": "猫粮不存在"}, status=status.HTTP_404_NOT_FOUND)

        favorite = CatFoodFavorite.objects.filter(user=request.user, catfood=catfood).first()

        if favorite:
            # 已收藏，取消收藏
            favorite.delete()
            return Response(
                {"detail": "取消收藏成功", "is_favorited": False}, status=status.HTTP_200_OK
            )
        else:
            # 未收藏，添加收藏
            favorite = CatFoodFavorite.objects.create(user=request.user, catfood=catfood)
            serializer = self.get_serializer(favorite)
            return Response(
                {"detail": "收藏成功", "is_favorited": True, "favorite": serializer.data},
                status=status.HTTP_201_CREATED,
            )

    @action(detail=False, methods=["post"], url_path="check")
    def check_favorite(self, request):
        """
        检查是否已收藏
        POST /api/catfood/favorites/check/
        Body: {"catfood_id": 1}
        """
        catfood_id = request.data.get("catfood_id")

        if not catfood_id:
            return Response({"error": "请提供 catfood_id"}, status=status.HTTP_400_BAD_REQUEST)

        is_favorited = CatFoodFavorite.objects.filter(
            user=request.user, catfood_id=catfood_id
        ).exists()

        return Response({"is_favorited": is_favorited}, status=status.HTTP_200_OK)
