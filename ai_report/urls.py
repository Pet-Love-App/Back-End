from django.urls import path
from .views import llm_chat
from .views import ingredient_info

urlpatterns = [
    path("llm/chat", llm_chat, name="ai_report_llm_chat"),
    path("ingredient/info", ingredient_info, name="ai_report_ingredient_info"),
]
