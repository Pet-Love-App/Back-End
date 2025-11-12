"""
猫粮相关路由
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CatFoodFavoriteViewSet, CatFoodViewSet

router = DefaultRouter()
# 注意：favorites 必须在空路径之前注册，避免路由冲突
router.register(r"favorites", CatFoodFavoriteViewSet, basename="catfood-favorite")
router.register(r"", CatFoodViewSet, basename="catfood")

urlpatterns = [
    path("", include(router.urls)),
]
