"""
评论相关路由 + 帖子/消息路由
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, PostViewSet, NotificationViewSet

router = DefaultRouter()
router.register(r"comments", CommentViewSet, basename="comment")
router.register(r"posts", PostViewSet, basename="post")
router.register(r"notifications", NotificationViewSet, basename="notification")

urlpatterns = [
    path("", include(router.urls)),
]
