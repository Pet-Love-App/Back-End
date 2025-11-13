"""
用户模块 URL 配置
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

# 创建路由器
router = DefaultRouter()
router.register(r"pets", views.PetViewSet, basename="pet")

urlpatterns = [
    # 用户信息
    path("me/", views.CurrentUserView.as_view(), name="current_user"),
    path("<int:user_id>/", views.UserDetailView.as_view(), name="user_detail"),
    # 头像上传
    path("avatar/", views.AvatarUploadView.as_view(), name="upload_avatar"),
    # 宠物相关（RESTful API）
    path("", include(router.urls)),
]
