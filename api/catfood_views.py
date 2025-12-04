"""
猫粮相关 API
使用 Supabase 进行数据操作
"""

import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from config.supabase_client import supabase_admin
from middleware.supabase_auth import get_current_user, require_auth
from services.supabase_storage import storage_service

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
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 20))
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
        result = query.order("created_at", desc=True).range(offset, offset + per_page - 1).execute()

        # 获取总数（用于分页）
        count_query = supabase_admin.table("catfoods").select("id", count="exact")
        if search:
            count_query = count_query.or_(f"name.ilike.%{search}%,brand.ilike.%{search}%")
        if brand:
            count_query = count_query.eq("brand", brand)
        count_result = count_query.execute()
        total = count_result.count if hasattr(count_result, "count") else len(result.data)

        return JsonResponse(
            {"catfoods": result.data, "page": page, "per_page": per_page, "total": total}
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
        catfood = (
            supabase_admin.table("catfoods").select("*").eq("id", catfood_id).single().execute()
        )

        if not catfood.data:
            return JsonResponse({"error": "Catfood not found"}, status=404)

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
            **catfood.data,
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
def create_catfood(request):
    """
    创建猫粮（需要管理员权限）

    POST /api/catfoods/create/
    Body: multipart/form-data
        - name: 猫粮名称
        - brand: 品牌
        - description: 描述
        - price: 价格
        - weight: 重量
        - image: 图片文件（可选）
        - ingredients: 成分列表 JSON
        - additives: 添加剂列表 JSON
        - tags: 标签列表 JSON
    """
    try:
        user = get_current_user(request)

        # 检查管理员权限
        profile = (
            supabase_admin.table("profiles").select("is_admin").eq("id", user.id).single().execute()
        )

        if not profile.data or not profile.data.get("is_admin"):
            return JsonResponse({"error": "Admin permission required"}, status=403)

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

        # 处理图片上传
        if "image" in request.FILES:
            image_file = request.FILES["image"]
            file_extension = image_file.name.split(".")[-1]

            # 先插入猫粮以获取 ID
            temp_result = supabase_admin.table("catfoods").insert(catfood_data).execute()
            catfood_id = temp_result.data[0]["id"]

            # 上传图片
            image_url = storage_service.upload_catfood_image(
                catfood_id, image_file.read(), file_extension
            )

            # 更新猫粮记录
            catfood_data["image_url"] = image_url
            result = (
                supabase_admin.table("catfoods")
                .update({"image_url": image_url})
                .eq("id", catfood_id)
                .execute()
            )
        else:
            # 直接插入
            result = supabase_admin.table("catfoods").insert(catfood_data).execute()
            catfood_id = result.data[0]["id"]

        # 处理成分
        ingredients = json.loads(request.POST.get("ingredients", "[]"))
        for ingredient in ingredients:
            ingredient_data = {
                "catfood_id": catfood_id,
                "ingredient_id": ingredient.get("ingredient_id"),
                "percentage": ingredient.get("percentage"),
            }
            supabase_admin.table("catfood_ingredients").insert(ingredient_data).execute()

        # 处理添加剂
        additives = json.loads(request.POST.get("additives", "[]"))
        for additive in additives:
            additive_data = {
                "catfood_id": catfood_id,
                "additive_id": additive.get("additive_id"),
            }
            supabase_admin.table("catfood_additives").insert(additive_data).execute()

        # 处理标签
        tags = json.loads(request.POST.get("tags", "[]"))
        for tag_name in tags:
            tag_data = {
                "catfood_id": catfood_id,
                "tag_name": tag_name,
            }
            supabase_admin.table("catfood_tag_relations").insert(tag_data).execute()

        return JsonResponse(
            {"message": "Catfood created successfully", "catfood_id": catfood_id}, status=201
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
@require_auth
def update_catfood(request, catfood_id):
    """
    更新猫粮信息（需要管理员权限）

    PUT /api/catfoods/<catfood_id>/
    """
    try:
        user = get_current_user(request)

        # 检查管理员权限
        profile = (
            supabase_admin.table("profiles").select("is_admin").eq("id", user.id).single().execute()
        )

        if not profile.data or not profile.data.get("is_admin"):
            return JsonResponse({"error": "Admin permission required"}, status=403)

        # 检查猫粮是否存在
        catfood = (
            supabase_admin.table("catfoods").select("*").eq("id", catfood_id).single().execute()
        )

        if not catfood.data:
            return JsonResponse({"error": "Catfood not found"}, status=404)

        data = json.loads(request.body)

        # 允许更新的字段
        allowed_fields = ["name", "brand", "description", "price", "weight", "image_url"]
        update_data = {k: v for k, v in data.items() if k in allowed_fields}

        if not update_data:
            return JsonResponse({"error": "No valid fields to update"}, status=400)

        # 更新
        result = supabase_admin.table("catfoods").update(update_data).eq("id", catfood_id).execute()

        return JsonResponse({"message": "Catfood updated successfully", "catfood": result.data[0]})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@require_auth
def delete_catfood(request, catfood_id):
    """
    删除猫粮（需要管理员权限）

    DELETE /api/catfoods/<catfood_id>/delete/
    """
    try:
        user = get_current_user(request)

        # 检查管理员权限
        profile = (
            supabase_admin.table("profiles").select("is_admin").eq("id", user.id).single().execute()
        )

        if not profile.data or not profile.data.get("is_admin"):
            return JsonResponse({"error": "Admin permission required"}, status=403)

        # 检查猫粮是否存在
        catfood = (
            supabase_admin.table("catfoods").select("*").eq("id", catfood_id).single().execute()
        )

        if not catfood.data:
            return JsonResponse({"error": "Catfood not found"}, status=404)

        # 删除猫粮图片（如果有）
        if catfood.data.get("image_url"):
            storage_service.delete_file_from_url(catfood.data["image_url"])

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
        data = json.loads(request.body)

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
            result = supabase_admin.table("catfood_ratings").insert(rating_data).execute()

        return JsonResponse({"message": "Rating submitted successfully", "rating": result.data[0]})

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
            return JsonResponse({"message": "Unfavorited successfully", "favorited": False})
        else:
            # 添加收藏
            favorite_data = {
                "catfood_id": catfood_id,
                "user_id": user.id,
            }
            supabase_admin.table("catfood_favorites").insert(favorite_data).execute()
            return JsonResponse({"message": "Favorited successfully", "favorited": True})

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
