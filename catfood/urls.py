"""
猫粮相关路由
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CatFoodFavoriteViewSet, CatFoodViewSet

router = DefaultRouter()
router.register(r"", CatFoodViewSet, basename="catfood")
router.register(r"favorites", CatFoodFavoriteViewSet, basename="catfood-favorite")

urlpatterns = [
    path("", include(router.urls)),
]
