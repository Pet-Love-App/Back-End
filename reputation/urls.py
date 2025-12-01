from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EquipBadgeView, UnequipBadgeView, BadgeViewSet, ReputationAdminViewSet

router = DefaultRouter()
router.register(r"badges", BadgeViewSet, basename="badge")
router.register(r"admin", ReputationAdminViewSet, basename="reputation_admin")

urlpatterns = [
    path("badges/<str:code>/equip/", EquipBadgeView.as_view(), name="equip_badge"),
    path("badges/<str:code>/unequip/", UnequipBadgeView.as_view(), name="unequip_badge"),
    path("", include(router.urls)),
]