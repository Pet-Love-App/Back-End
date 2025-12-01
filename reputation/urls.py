from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EquipBadgeView, UnequipBadgeView, BadgeViewSet, ReputationAdminViewSet,
    MyReputationView, UserReputationView, MyBadgesView,
)

router = DefaultRouter()
router.register(r"badges", BadgeViewSet, basename="badge")
router.register(r"admin", ReputationAdminViewSet, basename="reputation_admin")

urlpatterns = [
    # 信誉只读接口
    path("me/", MyReputationView.as_view(), name="my_reputation"),
    path("users/<int:user_id>/", UserReputationView.as_view(), name="user_reputation"),
    path("my-badges/", MyBadgesView.as_view(), name="my_badges"),

    # 佩戴/取消
    path("badges/<str:code>/equip/", EquipBadgeView.as_view(), name="equip_badge"),
    path("badges/<str:code>/unequip/", UnequipBadgeView.as_view(), name="unequip_badge"),

    # ViewSets
    path("", include(router.urls)),
]