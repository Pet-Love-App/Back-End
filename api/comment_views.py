"""
评论相关 API
使用 Supabase 进行数据操作
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from config.supabase_client import supabase_admin
from middleware.supabase_auth import get_current_user, require_auth
from utils import parse_json_body, safe_single


@csrf_exempt
@require_http_methods(["GET"])
def list_comments(request):
    """
    获取评论列表

    GET /api/comments/
    Query params:
        - target_type: post/catfood/report
        - target_id: 目标ID
    """
    try:
        target_type = request.GET.get("target_type")
        target_id = request.GET.get("target_id")

        if not target_type or not target_id:
            return JsonResponse(
                {"error": "target_type and target_id are required"}, status=400
            )

        # 查询评论，关联作者信息
        result = (
            supabase_admin.table("comments")
            .select("*, author:profiles(id, username, avatar_url)")
            .eq("target_type", target_type)
            .eq("target_id", target_id)
            .is_("parent_id", "null")  # 只查询顶级评论
            .order("created_at", desc=True)
            .execute()
        )

        # 为每个评论查询回复
        for comment in result.data:
            replies = (
                supabase_admin.table("comments")
                .select("*, author:profiles(id, username, avatar_url)")
                .eq("parent_id", comment["id"])
                .order("created_at")
                .execute()
            )
            comment["replies"] = replies.data

        return JsonResponse({"comments": result.data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def create_comment(request):
    """
    创建评论

    POST /api/comments/
    Body: {
        "target_type": "post",
        "target_id": 123,
        "content": "评论内容",
        "parent_id": null  // 可选，回复评论时使用
    }
    """
    try:
        user = get_current_user(request)
        try:
            data = parse_json_body(request)
        except ValueError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # 验证必填字段
        required_fields = ["target_type", "target_id", "content"]
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({"error": f"{field} is required"}, status=400)

        # 准备数据
        comment_data = {
            "author_id": user.id,
            "target_type": data["target_type"],
            "target_id": data["target_id"],
            "content": data["content"],
            "parent_id": data.get("parent_id"),
        }

        # 插入评论
        result = supabase_admin.table("comments").insert(comment_data).execute()

        # TODO: 创建通知
        # 如果是回复评论，通知被回复的用户
        # 如果是评论帖子，通知帖子作者

        return JsonResponse(
            {"message": "Comment created successfully", "comment": result.data[0]},
            status=201,
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@require_auth
def delete_comment(request, comment_id):
    """
    删除评论

    DELETE /api/comments/<comment_id>/
    """
    try:
        user = get_current_user(request)

        # 验证评论所有权
        comment_result = (
            supabase_admin.table("comments")
            .select("*")
            .eq("id", comment_id)
            .eq("author_id", user.id)
            .execute()
        )
        _, error = safe_single(comment_result, "Comment not found")
        if error:
            return JsonResponse({"error": error}, status=404)

        # 删除评论（回复会通过级联删除）
        supabase_admin.table("comments").delete().eq("id", comment_id).execute()

        return JsonResponse({"message": "Comment deleted successfully"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def like_comment(request, comment_id):
    """
    点赞/取消点赞评论

    POST /api/comments/<comment_id>/like/
    """
    try:
        user = get_current_user(request)

        # 检查是否已点赞
        existing = (
            supabase_admin.table("comment_likes")
            .select("id")
            .eq("comment_id", comment_id)
            .eq("user_id", user.id)
            .execute()
        )

        if existing.data:
            # 取消点赞
            supabase_admin.table("comment_likes").delete().eq(
                "id", existing.data[0]["id"]
            ).execute()
            return JsonResponse({"message": "Unliked successfully", "liked": False})
        else:
            # 添加点赞
            like_data = {
                "comment_id": comment_id,
                "user_id": user.id,
            }
            supabase_admin.table("comment_likes").insert(like_data).execute()
            return JsonResponse({"message": "Liked successfully", "liked": True})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
