"""
通知系统相关 API
使用 Supabase 进行数据操作
"""

import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from config.supabase_client import supabase_admin
from middleware.supabase_auth import get_current_user, require_auth


@csrf_exempt
@require_http_methods(["GET"])
@require_auth
def list_notifications(request):
    """
    获取当前用户的通知列表

    GET /api/notifications/
    Query params:
        - page: 页码（默认1）
        - per_page: 每页数量（默认20）
        - unread_only: 只显示未读（默认false）
    """
    try:
        user = get_current_user(request)

        # 安全地获取分页参数
        page = int(request.GET.get("page") or 1)
        per_page = int(request.GET.get("per_page") or 20)
        unread_only = request.GET.get("unread_only", "false").lower() == "true"

        # 计算偏移量
        offset = (page - 1) * per_page

        # 构建查询
        query = supabase_admin.table("notifications").select("*").eq("user_id", user.id)

        # 只显示未读
        if unread_only:
            query = query.eq("is_read", False)

        # 分页和排序
        result = (
            query.order("created_at", desc=True)
            .range(offset, offset + per_page - 1)
            .execute()
        )

        return JsonResponse(
            {"notifications": result.data, "page": page, "per_page": per_page}
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@require_auth
def get_unread_count(request):
    """
    获取未读通知数量

    GET /api/notifications/unread-count/
    """
    try:
        user = get_current_user(request)

        # 查询未读数量
        result = (
            supabase_admin.table("notifications")
            .select("id", count="exact")
            .eq("user_id", user.id)
            .eq("is_read", False)
            .execute()
        )

        count = result.count if hasattr(result, "count") else 0

        return JsonResponse({"unread_count": count})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def mark_as_read(request, notification_id):
    """
    标记通知为已读

    POST /api/notifications/<notification_id>/read/
    """
    try:
        user = get_current_user(request)

        # 验证通知所有权
        notification = (
            supabase_admin.table("notifications")
            .select("*")
            .eq("id", notification_id)
            .eq("user_id", user.id)
            .single()
            .execute()
        )

        if not notification.data:
            return JsonResponse({"error": "Notification not found"}, status=404)

        # 标记为已读
        supabase_admin.table("notifications").update({"is_read": True}).eq(
            "id", notification_id
        ).execute()

        return JsonResponse({"message": "Notification marked as read"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def mark_all_as_read(request):
    """
    标记所有通知为已读

    POST /api/notifications/read-all/
    """
    try:
        user = get_current_user(request)

        # 标记所有为已读
        supabase_admin.table("notifications").update({"is_read": True}).eq(
            "user_id", user.id
        ).eq("is_read", False).execute()

        return JsonResponse({"message": "All notifications marked as read"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@require_auth
def delete_notification(request, notification_id):
    """
    删除通知

    DELETE /api/notifications/<notification_id>/delete/
    """
    try:
        user = get_current_user(request)

        # 验证通知所有权
        notification = (
            supabase_admin.table("notifications")
            .select("*")
            .eq("id", notification_id)
            .eq("user_id", user.id)
            .single()
            .execute()
        )

        if not notification.data:
            return JsonResponse({"error": "Notification not found"}, status=404)

        # 删除通知
        supabase_admin.table("notifications").delete().eq(
            "id", notification_id
        ).execute()

        return JsonResponse({"message": "Notification deleted successfully"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@require_auth
def delete_all_notifications(request):
    """
    删除所有通知

    DELETE /api/notifications/delete-all/
    """
    try:
        user = get_current_user(request)

        # 删除所有通知
        supabase_admin.table("notifications").delete().eq("user_id", user.id).execute()

        return JsonResponse({"message": "All notifications deleted successfully"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_notification(request):
    """
    创建通知（系统内部接口）

    POST /api/notifications/create/
    Body: {
        "user_id": "uuid",
        "type": "comment",
        "title": "新评论",
        "content": "有人评论了你的帖子",
        "link": "/posts/123"
    }
    """
    try:
        # 注意：这个接口应该只允许系统内部调用，或者需要特殊权限
        # 这里简化处理，实际应该添加更严格的权限控制

        data = json.loads(request.body)

        user_id = data.get("user_id")
        notification_type = data.get("type")
        title = data.get("title")
        content = data.get("content")

        if not user_id or not notification_type or not title:
            return JsonResponse(
                {"error": "user_id, type, and title are required"}, status=400
            )

        # 准备通知数据
        notification_data = {
            "user_id": user_id,
            "type": notification_type,
            "title": title,
            "content": content,
            "link": data.get("link", ""),
            "is_read": False,
        }

        # 插入通知
        result = (
            supabase_admin.table("notifications").insert(notification_data).execute()
        )

        return JsonResponse(
            {
                "message": "Notification created successfully",
                "notification": result.data[0],
            },
            status=201,
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
