from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db import transaction

from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Badge, UserBadge, ReputationSummary
from .serializers import BadgeSerializer, UserBadgeSerializer, ReputationSummarySerializer
from .services import compute_user_reputation

User = get_user_model()


class EquipBadgeView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, code):
        badge = get_object_or_404(Badge, code=code)
        # 加行级锁，避免并发竞态
        ub = (
            UserBadge.objects.select_for_update()
            .filter(user=request.user, badge=badge)
            .first()
        )
        if not ub:
            return Response({"message": "你尚未获得该徽章，无法佩戴"}, status=status.HTTP_403_FORBIDDEN)

        # 若需要单佩戴策略，请取消注释以下代码：
        # UserBadge.objects.select_for_update().filter(user=request.user, is_equipped=True).update(is_equipped=False)

        if not ub.is_equipped:
            ub.is_equipped = True
            ub.save(update_fields=["is_equipped"])
        return Response({"message": f"已佩戴徽章：{badge.name}"}, status=status.HTTP_200_OK)


class UnequipBadgeView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, code):
        badge = get_object_or_404(Badge, code=code)
        ub = (
            UserBadge.objects.select_for_update()
            .filter(user=request.user, badge=badge)
            .first()
        )
        if not ub:
            return Response({"message": "你未拥有该徽章"}, status=status.HTTP_404_NOT_FOUND)
        if not ub.is_equipped:
            return Response({"message": "该徽章当前未佩戴"}, status=status.HTTP_200_OK)
        ub.is_equipped = False
        ub.save(update_fields=["is_equipped"])
        return Response({"message": f"已取消佩戴：{badge.name}"}, status=status.HTTP_200_OK)


class BadgeViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
        """
        徽章管理：
        - GET /reputation/badges/
        - GET /reputation/badges/{id}/
        - POST /reputation/badges/{id}/enable/
        - POST /reputation/badges/{id}/disable/
        """
        queryset = Badge.objects.all()
        serializer_class = BadgeSerializer

        def get_permissions(self):
            if self.action in ["enable", "disable"]:
                return [IsAdminUser()]
            # 列表/详情对所有已认证或匿名均可按需开放，这里默认允许任何人读取
            return [permissions.AllowAny()]

        @action(detail=True, methods=["post"], url_path="enable")
        def enable(self, request, pk=None):
            badge = self.get_object()
            badge.enabled = True
            badge.save(update_fields=["enabled"])
            return Response({"message": "已启用徽章"}, status=status.HTTP_200_OK)

        @action(detail=True, methods=["post"], url_path="disable")
        def disable(self, request, pk=None):
            badge = self.get_object()
            badge.enabled = False
            badge.save(update_fields=["enabled"])
            return Response({"message": "已禁用徽章"}, status=status.HTTP_200_OK)


class ReputationAdminViewSet(viewsets.ViewSet):
    """
    管理接口：
    - POST /reputation/admin/recompute_user/ { user_id }
    """
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=["post"], url_path="recompute_user")
    def recompute_user(self, request):
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"message": "缺少参数 user_id"}, status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, pk=user_id)
        summary = compute_user_reputation(user)
        data = ReputationSummarySerializer(summary).data
        return Response({"message": f"已重算用户 {user_id}", "summary": data}, status=status.HTTP_200_OK)