"""
用户相关视图
"""

from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Pet, UserProfile
from .serializers import (
    AvatarUploadSerializer,
    PetSerializer,
    UserProfileSerializer,
    UserSerializer,
)


class CurrentUserView(APIView):
    """获取当前用户信息"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """返回当前登录用户的信息（包含头像和宠物列表）"""
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)


class AvatarUploadView(APIView):
    """上传/删除用户头像"""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        """上传头像"""
        serializer = AvatarUploadSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        avatar_file = serializer.validated_data["avatar"]

        # 获取或创建用户资料
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        # 删除旧头像
        if profile.avatar:
            profile.avatar.delete(save=False)

        # 保存新头像
        profile.avatar = avatar_file
        profile.save()

        # 返回头像 URL
        avatar_url = request.build_absolute_uri(profile.avatar.url)

        return Response(
            {
                "message": "头像上传成功",
                "avatar": avatar_url,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request):
        """删除头像"""
        try:
            profile = request.user.profile
            if profile.avatar:
                profile.avatar.delete()
                profile.save()
                return Response({"message": "头像已删除"}, status=status.HTTP_200_OK)
            return Response({"message": "用户没有头像"}, status=status.HTTP_400_BAD_REQUEST)
        except UserProfile.DoesNotExist:
            return Response({"message": "用户资料不存在"}, status=status.HTTP_404_NOT_FOUND)


class UserDetailView(APIView):
    """获取用户详情（可以查看其他用户）"""

    def get(self, request, user_id):
        """根据用户 ID 获取用户信息"""
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user, context={"request": request})
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)


class PetViewSet(viewsets.ModelViewSet):
    """宠物 CRUD ViewSet"""

    serializer_class = PetSerializer
    permission_classes = [IsAuthenticated]
    # 同时支持 JSON 和 FormData（用于上传照片）
    # parser_classes = [MultiPartParser, FormParser]  # 移除限制，使用默认的 parsers

    def get_queryset(self):
        """只返回当前用户的宠物"""
        return Pet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """创建宠物时自动关联当前用户"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    def my_pets(self, request):
        """获取我的所有宠物"""
        pets = self.get_queryset()
        serializer = self.get_serializer(pets, many=True)
        return Response(serializer.data)
