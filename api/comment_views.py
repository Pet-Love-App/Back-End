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
        - target_type: post/catfood/report（可选，如果 my=true）
        - target_id: 目标ID（可选，如果 my=true）
        - my: true/false（获取当前用户的所有评论）
        - page: 页码（默认1）
        - page_size: 每页数量（默认20）
    """
    try:
        # 检查是否是获取当前用户的评论
        my_comments = request.GET.get("my", "").lower() == "true"

        if my_comments:
            # 获取当前用户的所有评论（需要认证）
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return JsonResponse({"error": "Authentication required"}, status=401)

            from middleware.supabase_auth import get_current_user

            try:
                user = get_current_user(request)
            except Exception:
                return JsonResponse({"error": "Invalid token"}, status=401)

            # 分页参数
            page = int(request.GET.get("page", 1))
            page_size = int(request.GET.get("page_size", 20))
            offset = (page - 1) * page_size

            # 查询当前用户的评论
            result = (
                supabase_admin.table("comments")
                .select("*, author:profiles(id, username, avatar_url)")
                .eq("author_id", user.id)
                .is_("parent_id", "null")  # 只查询顶级评论
                .order("created_at", desc=True)
                .range(offset, offset + page_size - 1)
                .execute()
            )

            # 为每个评论查询回复数量（可选）
            for comment in result.data:
                replies = (
                    supabase_admin.table("comments")
                    .select("id", count="exact")
                    .eq("parent_id", comment["id"])
                    .execute()
                )
                comment["reply_count"] = len(replies.data) if replies.data else 0

            return JsonResponse(
                {
                    "results": result.data,
                    "count": len(result.data),
                    "next": len(result.data) == page_size,
                    "previous": page > 1,
                }
            )

        # 原有逻辑：根据 target_type 和 target_id 获取评论
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
