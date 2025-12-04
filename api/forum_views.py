"""
论坛相关 API
使用 Supabase 进行数据操作
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from config.supabase_client import supabase_admin
from middleware.supabase_auth import get_current_user, require_auth
from services.supabase_storage import storage_service


@csrf_exempt
@require_http_methods(["GET"])
def list_posts(request):
    """
    获取帖子列表

    GET /api/posts/
    Query params:
        - page: 页码（默认1）
        - per_page: 每页数量（默认20）
    """
    try:
        # 安全地获取分页参数
        page = int(request.GET.get("page") or 1)
        per_page = int(request.GET.get("per_page") or 20)

        # 计算偏移量
        offset = (page - 1) * per_page

        # 查询帖子，关联作者和媒体
        result = (
            supabase_admin.table("posts")
            .select("*, author:profiles(id, username, avatar_url), media:post_media(*)")
            .order("created_at", desc=True)
            .range(offset, offset + per_page - 1)
            .execute()
        )

        return JsonResponse({"posts": result.data, "page": page, "per_page": per_page})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def create_post(request):
    """
    创建帖子

    POST /api/posts/
    Body: multipart/form-data
        - content: 文字内容
        - files: 图片/视频文件（可多个）
    """
    try:
        user = get_current_user(request)

        content = request.POST.get("content", "")

        # 创建帖子
        post_data = {
            "author_id": user.id,
            "content": content,
        }

        post_result = supabase_admin.table("posts").insert(post_data).execute()
        post_id = post_result.data[0]["id"]

        # 处理媒体文件
        media_urls = []
        files = request.FILES.getlist("files")

        for index, file in enumerate(files):
            # 检查文件类型
            if file.content_type.startswith("image/"):
                media_type = "image"
            elif file.content_type.startswith("video/"):
                media_type = "video"
            else:
                continue

            # 上传到 Supabase Storage
            file_extension = file.name.split(".")[-1]
            file_url = storage_service.upload_post_media(
                user.id, post_id, index, file.read(), file_extension
            )

            # 保存媒体记录
            media_data = {
                "post_id": post_id,
                "file_url": file_url,
                "media_type": media_type,
            }
            supabase_admin.table("post_media").insert(media_data).execute()
            media_urls.append(file_url)

        return JsonResponse(
            {
                "message": "Post created successfully",
                "post_id": post_id,
                "media_urls": media_urls,
            },
            status=201,
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@require_auth
def delete_post(request, post_id):
    """
    删除帖子

    DELETE /api/posts/<post_id>/
    """
    try:
        user = get_current_user(request)

        # 验证帖子所有权
        post = (
            supabase_admin.table("posts")
            .select("*")
            .eq("id", post_id)
            .eq("author_id", user.id)
            .single()
            .execute()
        )

        if not post.data:
            return JsonResponse({"error": "Post not found"}, status=404)

        # 查询并删除关联的媒体文件
        media = (
            supabase_admin.table("post_media")
            .select("file_url")
            .eq("post_id", post_id)
            .execute()
        )

        for media_item in media.data:
            if media_item.get("file_url"):
                storage_service.delete_file_from_url(media_item["file_url"])

        # 删除帖子（媒体记录会通过级联删除）
        supabase_admin.table("posts").delete().eq("id", post_id).execute()

        return JsonResponse({"message": "Post deleted successfully"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def favorite_post(request, post_id):
    """
    收藏/取消收藏帖子

    POST /api/posts/<post_id>/favorite/
    """
    try:
        user = get_current_user(request)

        # 检查是否已收藏
        existing = (
            supabase_admin.table("post_favorites")
            .select("id")
            .eq("post_id", post_id)
            .eq("user_id", user.id)
            .execute()
        )

        if existing.data:
            # 取消收藏
            supabase_admin.table("post_favorites").delete().eq(
                "id", existing.data[0]["id"]
            ).execute()
            return JsonResponse(
                {"message": "Unfavorited successfully", "favorited": False}
            )
        else:
            # 添加收藏
            favorite_data = {
                "post_id": post_id,
                "user_id": user.id,
            }
            supabase_admin.table("post_favorites").insert(favorite_data).execute()
            return JsonResponse(
                {"message": "Favorited successfully", "favorited": True}
            )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
