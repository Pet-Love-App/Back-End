from django.urls import path
from . import views

urlpatterns = [
    path("recognize/", views.ocr_recognize, name="ocr_recognize"),  # 识别接口
]