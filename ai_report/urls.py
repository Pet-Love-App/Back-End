from django.urls import path

from .views import (
    check_favorite_report,
    check_report_exists,
    delete_favorite_report,
    delete_report,
    get_favorite_reports,
    get_report,
    llm_chat,
    save_report,
    toggle_favorite_report,
)

urlpatterns = [
    # 原有的 LLM API（不修改）
    path("llm/chat", llm_chat, name="ai_report_llm_chat"),
    # 报告管理 API
    path("save/", save_report, name="save_report"),  # POST - 保存或更新报告
    path("<int:catfood_id>/", get_report, name="get_report"),  # GET - 获取报告
    path(
        "<int:catfood_id>/exists/", check_report_exists, name="check_report_exists"
    ),  # GET - 检查报告是否存在
    path(
        "<int:catfood_id>/delete/", delete_report, name="delete_report"
    ),  # DELETE - 删除报告（用于重新生成）
    # 报告收藏 API
    path("favorites/", get_favorite_reports, name="get_favorite_reports"),  # GET - 获取收藏列表
    path(
        "favorites/toggle/", toggle_favorite_report, name="toggle_favorite_report"
    ),  # POST - 切换收藏状态
    path(
        "favorites/<int:favorite_id>/", delete_favorite_report, name="delete_favorite_report"
    ),  # DELETE - 删除收藏
    path(
        "favorites/check/<int:report_id>/", check_favorite_report, name="check_favorite_report"
    ),  # GET - 检查是否已收藏
]
