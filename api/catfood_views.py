"""
猫粮相关 API
使用 Supabase 进行数据操作
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from config.supabase_client import supabase_admin
from middleware.supabase_auth import get_current_user, require_auth
from services.supabase_storage import storage_service
from utils import parse_json_body, parse_json_field, require_admin, safe_single

# ==================== 猫粮 CRUD ====================


@csrf_exempt
@require_http_methods(["GET"])
def list_catfoods(request):
    """
    获取猫粮列表（支持分页和搜索）

    GET /api/catfoods/
    Query params:
        - page: 页码（默认1）
        - per_page: 每页数量（默认20）
        - search: 搜索关键词（可选）
        - brand: 品牌筛选（可选）
        - tag: 标签筛选（可选）
    """
    try:
        # 安全地获取分页参数
        page = int(request.GET.get("page") or 1)
        per_page = int(request.GET.get("per_page") or 20)
        search = request.GET.get("search", "").strip()
        brand = request.GET.get("brand", "").strip()
        tag = request.GET.get("tag", "").strip()

        # 计算偏移量
        offset = (page - 1) * per_page

        # 构建查询
        query = supabase_admin.table("catfoods").select("*")

        # 搜索过滤
        if search:
            query = query.or_(f"name.ilike.%{search}%,brand.ilike.%{search}%")

        # 品牌过滤
        if brand:
            query = query.eq("brand", brand)

        # 标签过滤（需要关联查询）
        if tag:
            # 先查询有该标签的猫粮 ID
            tag_relations = (
                supabase_admin.table("catfood_tag_relations")
                .select("catfood_id")
                .eq("tag_name", tag)
                .execute()
            )
            catfood_ids = [r["catfood_id"] for r in tag_relations.data]
            if catfood_ids:
                query = query.in_("id", catfood_ids)
            else:
                # 没有匹配的猫粮
                return JsonResponse(
                    {"catfoods": [], "page": page, "per_page": per_page, "total": 0}
                )

        # 分页和排序
        result = (
            query.order("created_at", desc=True)
            .range(offset, offset + per_page - 1)
            .execute()
        )

        # 获取总数（用于分页）
        count_query = supabase_admin.table("catfoods").select("id", count="exact")
        if search:
            count_query = count_query.or_(
                f"name.ilike.%{search}%,brand.ilike.%{search}%"
            )
        if brand:
            count_query = count_query.eq("brand", brand)
        count_result = count_query.execute()
        total = (
            count_result.count if hasattr(count_result, "count") else len(result.data)
        )

        return JsonResponse(
            {
                "catfoods": result.data,
                "page": page,
                "per_page": per_page,
                "total": total,
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_catfood_detail(request, catfood_id):
    """
    获取猫粮详情

    GET /api/catfoods/<catfood_id>/
    """
    try:
        # 查询猫粮基本信息
        catfood_result = (
            supabase_admin.table("catfoods").select("*").eq("id", catfood_id).execute()
        )

        catfood_data, error = safe_single(catfood_result, "Catfood not found")
        if error:
            return JsonResponse({"error": error}, status=404)

        # 查询关联的成分
        ingredients = (
            supabase_admin.table("catfood_ingredients")
            .select("*, ingredient:ingredients(*)")
            .eq("catfood_id", catfood_id)
            .execute()
        )

        # 查询关联的添加剂
        additives = (
            supabase_admin.table("catfood_additives")
            .select("*, additive:additives(*)")
            .eq("catfood_id", catfood_id)
            .execute()
        )

        # 查询标签
        tags = (
            supabase_admin.table("catfood_tag_relations")
            .select("*, tag:catfood_tags(*)")
            .eq("catfood_id", catfood_id)
            .execute()
        )

        # 查询平均评分
        ratings = (
            supabase_admin.table("catfood_ratings")
            .select("score")
            .eq("catfood_id", catfood_id)
            .execute()
        )

        avg_rating = None
        rating_count = 0
        if ratings.data:
            rating_count = len(ratings.data)
            avg_rating = sum(r["score"] for r in ratings.data) / rating_count

        # 组合数据
        catfood_detail = {
            **catfood_data,
            "ingredients": ingredients.data,
            "additives": additives.data,
            "tags": tags.data,
            "avg_rating": avg_rating,
            "rating_count": rating_count,
        }

        return JsonResponse({"catfood": catfood_detail})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
@require_admin
def create_catfood(request):
    """
    创建猫粮（需要管理员权限）
    """
    try:
        # 获取基本信息
        name = request.POST.get("name")
        brand = request.POST.get("brand")

        if not name or not brand:
            return JsonResponse({"error": "Name and brand are required"}, status=400)

        # 准备猫粮数据
        catfood_data = {
            "name": name,
            "brand": brand,
            "description": request.POST.get("description", ""),
            "price": float(request.POST.get("price", 0)),
            "weight": float(request.POST.get("weight", 0)),
        }

        # 插入猫粮记录
        result = supabase_admin.table("catfoods").insert(catfood_data).execute()
        if not result.data:
            return JsonResponse({"error": "Failed to create catfood"}, status=500)

        catfood_id = result.data[0]["id"]

        # 处理图片上传
        if "image" in request.FILES:
            image_file = request.FILES["image"]
            file_extension = image_file.name.split(".")[-1]
            try:
                image_url = storage_service.upload_catfood_image(
                    catfood_id, image_file.read(), file_extension
                )
                supabase_admin.table("catfoods").update({"image_url": image_url}).eq(
                    "id", catfood_id
                ).execute()
            except Exception as e:
                print(f"Image upload failed: {e}")

        # 批量处理关联数据
        try:
            # 1. 成分
            ingredients = parse_json_field(request.POST.get("ingredients"))
            if ingredients:
                ing_data = [
                    {
                        "catfood_id": catfood_id,
                        "ingredient_id": item.get("ingredient_id"),
                        "percentage": item.get("percentage"),
                    }
                    for item in ingredients
                    if item.get("ingredient_id")
                ]
                if ing_data:
                    supabase_admin.table("catfood_ingredients").insert(
                        ing_data
                    ).execute()

            # 2. 添加剂
            additives = parse_json_field(request.POST.get("additives"))
            if additives:
                add_data = [
                    {
                        "catfood_id": catfood_id,
                        "additive_id": item.get("additive_id"),
                    }
                    for item in additives
                    if item.get("additive_id")
                ]
                if add_data:
                    supabase_admin.table("catfood_additives").insert(add_data).execute()

            # 3. 标签
            tags = parse_json_field(request.POST.get("tags"))
            if tags:
                tag_data = [
                    {"catfood_id": catfood_id, "tag_name": tag} for tag in tags if tag
                ]
                if tag_data:
                    supabase_admin.table("catfood_tag_relations").insert(
                        tag_data
                    ).execute()

        except Exception as e:
            print(f"Error saving relations: {e}")

        return JsonResponse(
            {"message": "Catfood created successfully", "catfood_id": catfood_id},
            status=201,
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
@require_auth
@require_admin
def update_catfood(request, catfood_id):
    """
    更新猫粮信息（需要管理员权限）

    支持部分字段更新，并可同时更新关联的成分/添加剂/标签
    """
    try:
        # 确认猫粮存在
        catfood_result = (
            supabase_admin.table("catfoods").select("*").eq("id", catfood_id).execute()
        )
        catfood_data, error = safe_single(catfood_result, "Catfood not found")
        if error:
            return JsonResponse({"error": error}, status=404)

        try:
            payload = parse_json_body(request, default={})
        except ValueError:
            return JsonResponse({"error": "Invalid JSON body"}, status=400)

        allowed_fields = {
            "name",
            "brand",
            "description",
            "price",
            "weight",
            "image_url",
        }
        update_data = {k: v for k, v in payload.items() if k in allowed_fields}

        if update_data:
            supabase_admin.table("catfoods").update(update_data).eq(
                "id", catfood_id
            ).execute()

        # 处理关联数据（如果提供）
        try:
            if "ingredients" in payload:
                supabase_admin.table("catfood_ingredients").delete().eq(
                    "catfood_id", catfood_id
                ).execute()
                ingredients = payload.get("ingredients") or []
                ing_data = [
                    {
                        "catfood_id": catfood_id,
                        "ingredient_id": item.get("ingredient_id"),
                        "percentage": item.get("percentage"),
                    }
                    for item in ingredients
                    if item.get("ingredient_id")
                ]
                if ing_data:
                    supabase_admin.table("catfood_ingredients").insert(
                        ing_data
                    ).execute()

            if "additives" in payload:
                supabase_admin.table("catfood_additives").delete().eq(
                    "catfood_id", catfood_id
                ).execute()
                additives = payload.get("additives") or []
                add_data = [
                    {
                        "catfood_id": catfood_id,
                        "additive_id": item.get("additive_id"),
                    }
                    for item in additives
                    if item.get("additive_id")
                ]
                if add_data:
                    supabase_admin.table("catfood_additives").insert(add_data).execute()

            if "tags" in payload:
                supabase_admin.table("catfood_tag_relations").delete().eq(
                    "catfood_id", catfood_id
                ).execute()
                tags = payload.get("tags") or []
                tag_data = [
                    {"catfood_id": catfood_id, "tag_name": tag} for tag in tags if tag
                ]
                if tag_data:
                    supabase_admin.table("catfood_tag_relations").insert(
                        tag_data
                    ).execute()

        except Exception as relation_err:
            print(f"Error updating relations for catfood {catfood_id}: {relation_err}")

        return JsonResponse({"message": "Catfood updated successfully"})

    except ValueError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@require_auth
@require_admin
def delete_catfood(request, catfood_id):
    """
    删除猫粮（需要管理员权限）

    DELETE /api/catfoods/<catfood_id>/delete/
    """
    try:
        catfood_result = (
            supabase_admin.table("catfoods").select("*").eq("id", catfood_id).execute()
        )
        catfood_data, error = safe_single(catfood_result, "Catfood not found")
        if error:
            return JsonResponse({"error": error}, status=404)

        # 删除猫粮图片（如果有）
        if catfood_data.get("image_url"):
            storage_service.delete_file_from_url(catfood_data["image_url"])

        # 删除猫粮（关联数据会通过级联删除）
        supabase_admin.table("catfoods").delete().eq("id", catfood_id).execute()

        return JsonResponse({"message": "Catfood deleted successfully"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ==================== 猫粮评分和收藏 ====================


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def rate_catfood(request, catfood_id):
    """
    评分猫粮

    POST /api/catfoods/<catfood_id>/rate/
    Body: {
        "score": 5,
        "comment": "很好吃"
    }
    """
    try:
        user = get_current_user(request)
        try:
            data = parse_json_body(request)
        except ValueError:
            return JsonResponse({"error": "Invalid JSON body"}, status=400)

        score = data.get("score")
        if not score or score < 1 or score > 5:
            return JsonResponse({"error": "Score must be between 1 and 5"}, status=400)

        # 检查是否已经评分
        existing = (
            supabase_admin.table("catfood_ratings")
            .select("id")
            .eq("catfood_id", catfood_id)
            .eq("user_id", user.id)
            .execute()
        )

        rating_data = {
            "catfood_id": catfood_id,
            "user_id": user.id,
            "score": score,
            "comment": data.get("comment", ""),
        }

        if existing.data:
            # 更新现有评分
            result = (
                supabase_admin.table("catfood_ratings")
                .update(rating_data)
                .eq("catfood_id", catfood_id)
                .eq("user_id", user.id)
                .execute()
            )
        else:
            # 创建新评分
            result = (
                supabase_admin.table("catfood_ratings").insert(rating_data).execute()
            )

        return JsonResponse(
            {"message": "Rating submitted successfully", "rating": result.data[0]}
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def favorite_catfood(request, catfood_id):
    """
    收藏/取消收藏猫粮

    POST /api/catfoods/<catfood_id>/favorite/
    """
    try:
        user = get_current_user(request)

        # 检查是否已收藏
        existing = (
            supabase_admin.table("catfood_favorites")
            .select("id")
            .eq("catfood_id", catfood_id)
            .eq("user_id", user.id)
            .execute()
        )

        if existing.data:
            # 取消收藏
            supabase_admin.table("catfood_favorites").delete().eq(
                "id", existing.data[0]["id"]
            ).execute()
            return JsonResponse(
                {"message": "Unfavorited successfully", "favorited": False}
            )
        else:
            # 添加收藏
            favorite_data = {
                "catfood_id": catfood_id,
                "user_id": user.id,
            }
            supabase_admin.table("catfood_favorites").insert(favorite_data).execute()
            return JsonResponse(
                {"message": "Favorited successfully", "favorited": True}
            )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@require_auth
def get_user_favorites(request):
    """
    获取用户收藏的猫粮列表

    GET /api/catfoods/favorites/
    """
    try:
        user = get_current_user(request)

        # 查询收藏，并关联猫粮信息
        result = (
            supabase_admin.table("catfood_favorites")
            .select("*, catfood:catfoods(*)")
            .eq("user_id", user.id)
            .order("created_at", desc=True)
            .execute()
        )

        return JsonResponse({"favorites": result.data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_catfood_ratings(request, catfood_id):
    """
    获取猫粮的评分列表

    GET /api/catfoods/<catfood_id>/ratings/
    """
    try:
        # 查询评分，并关联用户信息
        result = (
            supabase_admin.table("catfood_ratings")
            .select("*, user:profiles(username, avatar_url)")
            .eq("catfood_id", catfood_id)
            .order("created_at", desc=True)
            .execute()
        )

        return JsonResponse({"ratings": result.data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ==================== 猫粮点赞功能 ====================


@csrf_exempt
@require_http_methods(["GET"])
@require_auth
def list_catfood_likes(request):
    """
    获取用户的点赞列表

    GET /api/catfood/likes/
    """
    try:
        user = get_current_user(request)

        # 查询点赞，并关联猫粮信息
        result = (
            supabase_admin.table("catfood_likes")
            .select("*, catfood:catfoods(*)")
            .eq("user_id", user.id)
            .order("created_at", desc=True)
            .execute()
        )

        return JsonResponse({"likes": result.data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def like_catfood(request):
    """
    点赞猫粮

    POST /api/catfood/likes/
    Body: {"catfood_id": 1}
    """
    try:
        user = get_current_user(request)
        try:
            data = parse_json_body(request)
        except ValueError:
            return JsonResponse({"error": "Invalid JSON body"}, status=400)
        catfood_id = data.get("catfood_id")

        if not catfood_id:
            return JsonResponse({"error": "catfood_id is required"}, status=400)

        # 检查猫粮是否存在
        catfood_result = (
            supabase_admin.table("catfoods").select("id").eq("id", catfood_id).execute()
        )
        _, error = safe_single(catfood_result, "Catfood not found")
        if error:
            return JsonResponse({"error": error}, status=404)

        # 检查是否已点赞
        existing = (
            supabase_admin.table("catfood_likes")
            .select("id")
            .eq("user_id", user.id)
            .eq("catfood_id", catfood_id)
            .execute()
        )

        if existing.data:
            return JsonResponse({"error": "Already liked"}, status=400)

        # 创建点赞
        like_data = {"user_id": user.id, "catfood_id": catfood_id}
        result = supabase_admin.table("catfood_likes").insert(like_data).execute()

        return JsonResponse(
            {"message": "Liked successfully", "like": result.data[0]}, status=201
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@require_auth
def unlike_catfood(request, like_id):
    """
    取消点赞

    DELETE /api/catfood/likes/<like_id>/
    """
    try:
        user = get_current_user(request)

        # 检查点赞是否存在且属于当前用户
        like_result = (
            supabase_admin.table("catfood_likes")
            .select("*")
            .eq("id", like_id)
            .eq("user_id", user.id)
            .execute()
        )
        like_data, error = safe_single(like_result, "Like not found")
        if error:
            return JsonResponse({"error": error}, status=404)

        # 删除点赞
        supabase_admin.table("catfood_likes").delete().eq(
            "id", like_data["id"]
        ).execute()

        return JsonResponse({"message": "Unliked successfully"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def toggle_like_catfood(request):
    """
    切换点赞状态（点赞/取消点赞）

    POST /api/catfood/likes/toggle/
    Body: {"catfood_id": 1}
    """
    try:
        user = get_current_user(request)
        try:
            data = parse_json_body(request)
        except ValueError:
            return JsonResponse({"error": "Invalid JSON body"}, status=400)
        catfood_id = data.get("catfood_id")

        if not catfood_id:
            return JsonResponse({"error": "catfood_id is required"}, status=400)

        # 检查猫粮是否存在
        catfood_result = (
            supabase_admin.table("catfoods").select("id").eq("id", catfood_id).execute()
        )
        _, error = safe_single(catfood_result, "Catfood not found")
        if error:
            return JsonResponse({"error": error}, status=404)

        # 检查是否已点赞
        existing = (
            supabase_admin.table("catfood_likes")
            .select("id")
            .eq("user_id", user.id)
            .eq("catfood_id", catfood_id)
            .execute()
        )

        if existing.data:
            # 取消点赞
            supabase_admin.table("catfood_likes").delete().eq(
                "id", existing.data[0]["id"]
            ).execute()
            return JsonResponse({"message": "Unliked successfully", "liked": False})
        else:
            # 点赞
            like_data = {"user_id": user.id, "catfood_id": catfood_id}
            supabase_admin.table("catfood_likes").insert(like_data).execute()
            return JsonResponse({"message": "Liked successfully", "liked": True})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def check_like_status(request):
    """
    检查点赞状态

    POST /api/catfood/likes/check/
    Body: {"catfood_id": 1}
    """
    try:
        user = get_current_user(request)
        data = parse_json_body(request)
        catfood_id = data.get("catfood_id")

        if not catfood_id:
            return JsonResponse({"error": "catfood_id is required"}, status=400)

        # 检查是否已点赞
        existing = (
            supabase_admin.table("catfood_likes")
            .select("id")
            .eq("user_id", user.id)
            .eq("catfood_id", catfood_id)
            .execute()
        )

        return JsonResponse({"liked": bool(existing.data)})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_catfood_likes_count(request, catfood_id):
    """
    获取猫粮的点赞数量

    GET /api/catfood/likes/count/<catfood_id>/
    """
    try:
        # 查询点赞数量
        result = (
            supabase_admin.table("catfood_likes")
            .select("id", count="exact")
            .eq("catfood_id", catfood_id)
            .execute()
        )

        return JsonResponse(
            {"catfood_id": catfood_id, "likes_count": result.count or 0}
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ==================== 条形码功能 ====================


@csrf_exempt
@require_http_methods(["GET"])
def get_catfood_by_barcode(request):
    """
    通过条形码查询猫粮

    GET /api/catfood/by-barcode/?barcode=1234567890
    """
    try:
        barcode = request.GET.get("barcode", "").strip()

        if not barcode:
            return JsonResponse({"error": "Barcode is required"}, status=400)

        # 查询猫粮
        result = (
            supabase_admin.table("catfoods")
            .select("*")
            .eq("barcode", barcode)
            .execute()
        )

        if not result.data:
            return JsonResponse({"error": "Catfood not found"}, status=404)

        return JsonResponse({"catfood": result.data[0]})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def scan_barcode(request):
    """
    扫描条形码（通过 OCR 识别图片中的条形码）

    POST /api/catfood/scan-barcode/
    Body: multipart/form-data with "image" file
    """
    try:
        if "image" not in request.FILES:
            return JsonResponse({"error": "Image file is required"}, status=400)

        image_file = request.FILES["image"]

        # 检查文件类型
        allowed_types = ["image/jpeg", "image/png", "image/jpg"]
        if image_file.content_type not in allowed_types:
            return JsonResponse(
                {"error": "Invalid file type. Only JPEG, PNG allowed"}, status=400
            )

        # 检查文件大小（最大 5MB）
        if image_file.size > 5 * 1024 * 1024:
            return JsonResponse(
                {"error": "File too large. Maximum size is 5MB"}, status=400
            )

        # TODO: 集成条形码识别库（如 pyzbar）
        # 目前返回提示信息
        return JsonResponse(
            {
                "error": "Barcode scanning not yet implemented",
                "message": "Please use the barcode query API with a known barcode",
            },
            status=501,
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ==================== 猫粮评论快捷接口 ====================


@csrf_exempt
@require_http_methods(["GET"])
def get_catfood_comments(request, catfood_id):
    """
    获取猫粮的所有评论

    GET /api/catfood/<catfood_id>/comments/
    Query params:
        - page: 页码（默认1）
        - per_page: 每页数量（默认20）
    """
    try:
        # 安全地获取分页参数
        page = int(request.GET.get("page") or 1)
        per_page = int(request.GET.get("per_page") or 20)
        offset = (page - 1) * per_page

        # 检查猫粮是否存在
        catfood_result = (
            supabase_admin.table("catfoods").select("id").eq("id", catfood_id).execute()
        )
        _, error = safe_single(catfood_result, "Catfood not found")
        if error:
            return JsonResponse({"error": error}, status=404)

        # 查询评论，并关联用户信息
        result = (
            supabase_admin.table("comments")
            .select("*, user:profiles(id, username, avatar_url)")
            .eq("target_type", "catfood")
            .eq("target_id", catfood_id)
            .order("created_at", desc=True)
            .range(offset, offset + per_page - 1)
            .execute()
        )

        # 获取总数
        count_result = (
            supabase_admin.table("comments")
            .select("id", count="exact")
            .eq("target_type", "catfood")
            .eq("target_id", catfood_id)
            .execute()
        )

        return JsonResponse(
            {
                "comments": result.data,
                "total": count_result.count or 0,
                "page": page,
                "per_page": per_page,
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
