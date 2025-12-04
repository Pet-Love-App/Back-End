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

        # 批量查询点赞数量（为每个猫粮添加 like_count）
        if result.data:
            catfood_ids = [cf["id"] for cf in result.data]

            # 查询所有相关的点赞记录
            likes_result = (
                supabase_admin.table("catfood_likes")
                .select("catfood_id")
                .in_("catfood_id", catfood_ids)
                .execute()
            )

            # 统计每个猫粮的点赞数
            like_counts = {}
            for like in likes_result.data:
                catfood_id = like["catfood_id"]
                like_counts[catfood_id] = like_counts.get(catfood_id, 0) + 1

            # 为每个猫粮添加点赞数和 percentData
            for catfood in result.data:
                catfood["like_count"] = like_counts.get(catfood["id"], 0)

                # 组装 percentData（只包含非 null 的字段）
                percent_data = {}
                fields_to_check = {
                    "crude_protein": catfood.get("crude_protein"),
                    "crude_fat": catfood.get("crude_fat"),
                    "carbohydrates": catfood.get("carbohydrates"),
                    "crude_fiber": catfood.get("crude_fiber"),
                    "crude_ash": catfood.get("crude_ash"),
                    "others": catfood.get("others"),
                }
                for key, value in fields_to_check.items():
                    if value is not None:
                        percent_data[key] = value
                catfood["percentData"] = percent_data

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

        # 查询点赞数量
        likes = (
            supabase_admin.table("catfood_likes")
            .select("id", count="exact")
            .eq("catfood_id", catfood_id)
            .execute()
        )
        like_count = likes.count if hasattr(likes, "count") else 0

        # 组装 percentData（参考旧项目逻辑）
        # 只包含非 null 的字段（前端使用 Object.keys() 遍历）
        percent_data = {}
        fields_to_check = {
            "crude_protein": catfood_data.get("crude_protein"),
            "crude_fat": catfood_data.get("crude_fat"),
            "carbohydrates": catfood_data.get("carbohydrates"),
            "crude_fiber": catfood_data.get("crude_fiber"),
            "crude_ash": catfood_data.get("crude_ash"),
            "others": catfood_data.get("others"),
        }
        # 只添加非 null 的字段
        for key, value in fields_to_check.items():
            if value is not None:
                percent_data[key] = value

        # 展平嵌套的 ingredients 和 additives 数据（参考旧项目逻辑）
        # 后端查询返回：[{ingredient_id: 1, ingredient: {...}}, ...]
        # 前端期望：[{id, name, type, ...}, ...]
        ingredient_list = []
        for item in ingredients.data:
            if item.get("ingredient"):
                ingredient_list.append(item["ingredient"])

        additive_list = []
        for item in additives.data:
            if item.get("additive"):
                additive_list.append(item["additive"])

        # 展平标签数据
        tag_list = []
        for item in tags.data:
            if item.get("tag"):
                tag_list.append(item["tag"]["name"])

        # 组合数据
        catfood_detail = {
            **catfood_data,
            "ingredient": ingredient_list,  # 使用扁平的成分列表
            "additive": additive_list,  # 使用扁平的添加剂列表
            "tags": tag_list,  # 使用标签名称列表
            "avg_rating": avg_rating,
            "rating_count": rating_count,
            "like_count": like_count,
            "percentData": percent_data,
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
def update_catfood(request, catfood_id):
    """
    更新猫粮信息

    权限规则：
    - 更新基本信息（名称、品牌等）：需要管理员权限
    - 更新关联数据（成分、添加剂）：所有登录用户均可
    """
    try:
        user = get_current_user(request)

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

        # 检查是否只更新关联数据（成分/添加剂/标签）
        relation_only_fields = {"ingredient", "additive", "tags"}
        is_relation_only = all(k in relation_only_fields for k in payload.keys())

        # 如果更新基本字段，需要管理员权限
        if not is_relation_only:
            # 检查管理员权限
            try:
                profile_result = (
                    supabase_admin.table("user_profiles")
                    .select("is_admin")
                    .eq("user_id", user.id)
                    .execute()
                )
                is_admin = False
                if profile_result.data:
                    is_admin = profile_result.data[0].get("is_admin", False)

                if not is_admin:
                    return JsonResponse(
                        {"error": "Admin permission required"},
                        status=403,
                    )
            except Exception:
                return JsonResponse(
                    {"error": "Failed to check permissions"},
                    status=500,
                )

        # 允许更新的字段（基本信息和营养分析）
        allowed_fields = {
            "name",
            "brand",
            "description",
            "price",
            "weight",
            "image_url",
            "barcode",
            # 营养分析字段
            "percentage",
            "safety",
            "nutrient",
            # 营养成分百分比字段（从 percent_data 解包）
            "crude_protein",
            "crude_fat",
            "carbohydrates",
            "crude_fiber",
            "crude_ash",
            "others",
        }

        # 处理 percent_data（参考旧项目逻辑）
        # 如果提供了 percentData 或 percent_data，将其解包到各个营养成分字段
        percent_data = payload.pop("percentData", None) or payload.pop(
            "percent_data", None
        )
        if percent_data and isinstance(percent_data, dict):
            # 字段名映射表：AI返回的简短字段名 -> 数据库完整字段名
            # 注意：数据库只有以下6个营养成分字段
            field_mapping = {
                "protein": "crude_protein",
                "fat": "crude_fat",
                "fiber": "crude_fiber",
                "ash": "crude_ash",
                # 这些字段名相同，无需映射
                "crude_protein": "crude_protein",
                "crude_fat": "crude_fat",
                "crude_fiber": "crude_fiber",
                "crude_ash": "crude_ash",
                "carbohydrates": "carbohydrates",
                "others": "others",
                # moisture 字段在数据库中不存在，忽略
            }

            # 将 percent_data 的各个字段添加到 payload 中（带字段名映射）
            for ai_key, db_key in field_mapping.items():
                if ai_key in percent_data and percent_data[ai_key] is not None:
                    if db_key in allowed_fields:
                        payload[db_key] = percent_data[ai_key]

        # 筛选出允许更新的字段
        update_data = {
            k: v for k, v in payload.items() if k in allowed_fields and v is not None
        }

        if update_data:
            supabase_admin.table("catfoods").update(update_data).eq(
                "id", catfood_id
            ).execute()

        # 处理关联数据（如果提供）
        # 支持两种格式：
        # 1. 简单ID数组：{"ingredient": [1, 2, 3]}（前端扫描功能使用）
        # 2. 对象数组：{"ingredients": [{"ingredient_id": 1, "percentage": 10}]}（完整格式）
        try:
            # 处理成分关联（兼容 ingredient 和 ingredients 两种字段名）
            ingredient_data = payload.get("ingredient") or payload.get("ingredients")
            if ingredient_data is not None:
                # 删除旧关联
                supabase_admin.table("catfood_ingredients").delete().eq(
                    "catfood_id", catfood_id
                ).execute()

                if ingredient_data:
                    # 判断是简单ID数组还是对象数组
                    if isinstance(ingredient_data[0], (int, str)):
                        # 简单ID数组格式
                        ing_data = [
                            {
                                "catfood_id": catfood_id,
                                "ingredient_id": int(ing_id),
                                "order": idx,
                            }
                            for idx, ing_id in enumerate(ingredient_data)
                        ]
                    else:
                        # 对象数组格式
                        ing_data = [
                            {
                                "catfood_id": catfood_id,
                                "ingredient_id": item.get("ingredient_id"),
                                "percentage": item.get("percentage"),
                                "order": idx,
                            }
                            for idx, item in enumerate(ingredient_data)
                            if item.get("ingredient_id")
                        ]

                    if ing_data:
                        supabase_admin.table("catfood_ingredients").insert(
                            ing_data
                        ).execute()

            # 处理添加剂关联（兼容 additive 和 additives 两种字段名）
            additive_data = payload.get("additive") or payload.get("additives")
            if additive_data is not None:
                # 删除旧关联
                supabase_admin.table("catfood_additives").delete().eq(
                    "catfood_id", catfood_id
                ).execute()

                if additive_data:
                    # 判断是简单ID数组还是对象数组
                    if isinstance(additive_data[0], (int, str)):
                        # 简单ID数组格式
                        add_data = [
                            {
                                "catfood_id": catfood_id,
                                "additive_id": int(add_id),
                                "order": idx,
                            }
                            for idx, add_id in enumerate(additive_data)
                        ]
                    else:
                        # 对象数组格式
                        add_data = [
                            {
                                "catfood_id": catfood_id,
                                "additive_id": item.get("additive_id"),
                                "order": idx,
                            }
                            for idx, item in enumerate(additive_data)
                            if item.get("additive_id")
                        ]

                    if add_data:
                        supabase_admin.table("catfood_additives").insert(
                            add_data
                        ).execute()

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
@require_http_methods(["GET"])
@require_auth
def get_my_rating(request, catfood_id):
    """
    获取当前用户对指定猫粮的评分

    GET /api/catfoods/<catfood_id>/my-rating/
    """
    try:
        user = get_current_user(request)

        # 查询用户的评分
        result = (
            supabase_admin.table("catfood_ratings")
            .select("*")
            .eq("catfood_id", catfood_id)
            .eq("user_id", user.id)
            .execute()
        )

        if result.data:
            return JsonResponse({"rating": result.data[0]})
        else:
            return JsonResponse({"rating": None})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@require_auth
def delete_rating(request, rating_id):
    """
    删除评分

    DELETE /api/catfoods/ratings/<rating_id>/
    """
    try:
        user = get_current_user(request)

        # 查询评分，确保是当前用户的评分
        result = (
            supabase_admin.table("catfood_ratings")
            .select("*")
            .eq("id", rating_id)
            .eq("user_id", user.id)
            .execute()
        )

        if not result.data:
            return JsonResponse(
                {"error": "Rating not found or not owned by user"}, status=404
            )

        # 删除评分
        supabase_admin.table("catfood_ratings").delete().eq("id", rating_id).execute()

        return JsonResponse({"message": "Rating deleted successfully"})

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

        # 转换字段名：将嵌套的 catfood 对象中的 image_url 转换为 imageUrl
        favorites_data = result.data
        for favorite in favorites_data:
            if favorite.get("catfood") and isinstance(favorite["catfood"], dict):
                catfood = favorite["catfood"]
                # 转换字段名（蛇形 -> 驼峰）
                if "image_url" in catfood:
                    catfood["imageUrl"] = catfood.pop("image_url")
                if "count_num" in catfood:
                    catfood["countNum"] = catfood.pop("count_num")
                if "created_at" in catfood:
                    catfood["createdAt"] = catfood.pop("created_at")
                if "updated_at" in catfood:
                    catfood["updatedAt"] = catfood.pop("updated_at")

                # 组装 percentData（只包含非 null 的字段）
                percent_data = {}
                fields_to_check = {
                    "crude_protein": catfood.get("crude_protein"),
                    "crude_fat": catfood.get("crude_fat"),
                    "carbohydrates": catfood.get("carbohydrates"),
                    "crude_fiber": catfood.get("crude_fiber"),
                    "crude_ash": catfood.get("crude_ash"),
                    "others": catfood.get("others"),
                }
                for key, value in fields_to_check.items():
                    if value is not None:
                        percent_data[key] = value
                catfood["percentData"] = percent_data

        return JsonResponse({"favorites": favorites_data})

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
@require_http_methods(["GET", "POST"])
@require_auth
def catfood_likes(request):
    """
    GET /api/catfood/likes/   -> 获取点赞列表
    POST /api/catfood/likes/  -> 点赞猫粮
    """
    try:
        user = get_current_user(request)

        if request.method == "GET":
            result = (
                supabase_admin.table("catfood_likes")
                .select("*, catfood:catfoods(*)")
                .eq("user_id", user.id)
                .order("created_at", desc=True)
                .execute()
            )
            return JsonResponse({"likes": result.data})

        try:
            data = parse_json_body(request)
        except ValueError:
            return JsonResponse({"error": "Invalid JSON body"}, status=400)

        catfood_id = data.get("catfood_id")
        if not catfood_id:
            return JsonResponse({"error": "catfood_id is required"}, status=400)

        catfood_result = (
            supabase_admin.table("catfoods").select("id").eq("id", catfood_id).execute()
        )
        _, error = safe_single(catfood_result, "Catfood not found")
        if error:
            return JsonResponse({"error": error}, status=404)

        existing = (
            supabase_admin.table("catfood_likes")
            .select("id")
            .eq("user_id", user.id)
            .eq("catfood_id", catfood_id)
            .execute()
        )
        if existing.data:
            return JsonResponse({"error": "Already liked"}, status=400)

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

        return JsonResponse({"catfood_id": catfood_id, "like_count": result.count or 0})

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
