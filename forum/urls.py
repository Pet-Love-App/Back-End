"""
论坛系统路由
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NotificationViewSet, PostViewSet

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")
router.register(r"notifications", NotificationViewSet, basename="notification")

urlpatterns = [
    path("", include(router.urls)),
]
