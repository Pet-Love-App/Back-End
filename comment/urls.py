"""
评论相关路由
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet

router = DefaultRouter()
router.register(r"", CommentViewSet, basename="comment")

urlpatterns = [
    path("", include(router.urls)),
]
