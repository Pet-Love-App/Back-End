from django.urls import path

from .views import (
    check_report_exists,
    delete_report,
    get_report,
    llm_chat,
    save_report,
)

urlpatterns = [
    # 原有的 LLM API（不修改）
    path("llm/chat", llm_chat, name="ai_report_llm_chat"),

    # 新增的报告管理 API
    path("save/", save_report, name="save_report"),  # POST - 保存或更新报告
    path("<int:catfood_id>/", get_report, name="get_report"),  # GET - 获取报告
    path("<int:catfood_id>/exists/", check_report_exists, name="check_report_exists"),  # GET - 检查报告是否存在
    path("<int:catfood_id>/delete/", delete_report, name="delete_report"),  # DELETE - 删除报告（用于重新生成）
]

