"""
猫粮相关路由
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CatFoodViewSet

router = DefaultRouter()
router.register(r"", CatFoodViewSet, basename="catfood")

urlpatterns = [
    path("", include(router.urls)),
]
