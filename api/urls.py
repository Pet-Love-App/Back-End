"""
精简后的 API URL 配置
只保留必要的端点（AI 报告、OCR、搜索）
"""

from django.http import JsonResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import ai_views, ocr_views, search_views


@csrf_exempt
def debug_test(request):
    """调试测试端点"""
    return JsonResponse(
        {
            "ok": True,
            "method": request.method,
            "content_type": request.content_type,
            "body_size": len(request.body) if request.body else 0,
            "headers": {
                "Authorization": request.META.get("HTTP_AUTHORIZATION", "")[:50] + "..."
                if request.META.get("HTTP_AUTHORIZATION")
                else None,
                "Content-Type": request.META.get("CONTENT_TYPE"),
            },
        }
    )


urlpatterns = [
    # 调试端点
    path("debug/test/", debug_test, name="debug_test"),
    # ==================== AI 报告服务 ====================
    path("ai/llm/chat/", ai_views.llm_chat, name="ai_llm_chat"),
    path("ai/save/", ai_views.save_report, name="ai_save_report"),
    path("ai/<int:catfood_id>/", ai_views.get_report, name="ai_get_report"),
    path(
        "ai/<int:catfood_id>/exists/",
        ai_views.check_report_exists,
        name="ai_check_report_exists",
    ),
    path(
        "ai/<int:catfood_id>/delete/",
        ai_views.delete_report,
        name="ai_delete_report",
    ),
    # AI 报告收藏功能
    path(
        "ai/favorites/",
        ai_views.get_favorite_reports,
        name="ai_get_favorite_reports",
    ),
    path(
        "ai/favorites/toggle/",
        ai_views.toggle_favorite_report,
        name="ai_toggle_favorite_report",
    ),
    path(
        "ai/favorites/<int:favorite_id>/",
        ai_views.delete_favorite_report,
        name="ai_delete_favorite_report",
    ),
    path(
        "ai/favorites/check/<int:report_id>/",
        ai_views.check_favorite_report,
        name="ai_check_favorite_report",
    ),
    # ==================== OCR 识别服务 ====================
    path("ocr/recognize/", ocr_views.ocr_recognize, name="ocr_recognize"),
    # ==================== 搜索服务 ====================
    path(
        "search/ingredient/info",
        search_views.search_ingredient_info,
        name="search_ingredient_info",
    ),
]
