from django.urls import path
from .views import llm_chat

urlpatterns = [
    path("llm/chat", llm_chat, name="ai_report_llm_chat"),
]
