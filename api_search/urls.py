from django.urls import path
from .views import ingredient_info

urlpatterns = [
    path("ingredient/info", ingredient_info, name="ai_report_ingredient_info"),
]
