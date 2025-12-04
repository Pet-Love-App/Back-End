"""
信誉系统相关 API
使用 Supabase 进行数据操作
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from config.supabase_client import supabase_admin
from middleware.supabase_auth import get_current_user, require_auth
from utils import get_single_or_none, parse_json_body, require_admin, safe_single


@csrf_exempt
@require_http_methods(["GET"])
@require_auth
def get_my_reputation(request):
    """
    获取当前用户的信誉信息

    GET /api/reputation/me/
    """
    try:
        user = get_current_user(request)

        # 查询信誉信息
        reputation_result = (
            supabase_admin.table("reputation_summaries")
            .select("*")
            .eq("user_id", user.id)
            .execute()
        )
        reputation_data = get_single_or_none(reputation_result)

        if not reputation_data:
            # 如果不存在，创建默认信誉记录
            default_reputation = {
                "user_id": user.id,
                "score": 0,
                "level": "novice",
            }
            insert_result = (
                supabase_admin.table("reputation_summaries")
                .insert(default_reputation)
                .execute()
            )
            reputation_data = insert_result.data[0]

        return JsonResponse({"reputation": reputation_data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_user_reputation(request, user_id):
    """
    获取指定用户的信誉信息

    GET /api/reputation/users/<user_id>/
    """
    try:
        # 查询信誉信息
        reputation_result = (
            supabase_admin.table("reputation_summaries")
            .select("*, user:profiles(username, avatar_url)")
            .eq("user_id", user_id)
            .execute()
        )
        reputation_data, error = safe_single(reputation_result, "Reputation not found")
        if error:
            return JsonResponse({"error": error}, status=404)

        return JsonResponse({"reputation": reputation_data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@require_auth
def get_my_badges(request):
    """
    获取当前用户的徽章列表

    GET /api/reputation/my-badges/
    """
    try:
        user = get_current_user(request)

        # 查询用户徽章
        user_badges = (
            supabase_admin.table("user_badges")
            .select("*, badge:badges(*)")
            .eq("user_id", user.id)
            .order("earned_at", desc=True)
            .execute()
        )

        return JsonResponse({"badges": user_badges.data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def list_all_badges(request):
    """
    获取所有可用徽章列表

    GET /api/reputation/badges/
    """
    try:
        # 查询所有徽章
        badges = (
            supabase_admin.table("badges")
            .select("*")
            .order("required_score", desc=False)
            .execute()
        )

        return JsonResponse({"badges": badges.data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def equip_badge(request, badge_code):
    """
    佩戴徽章

    POST /api/reputation/badges/<badge_code>/equip/
    """
    try:
        user = get_current_user(request)

        # 检查用户是否拥有该徽章
        user_badge_result = (
            supabase_admin.table("user_badges")
            .select("id")
            .eq("user_id", user.id)
            .eq("badge_code", badge_code)
            .execute()
        )
        user_badge_data, error = safe_single(
            user_badge_result, "You don't have this badge"
        )
        if error:
            return JsonResponse({"error": error}, status=404)

        # 取消其他徽章的佩戴状态
        supabase_admin.table("user_badges").update({"is_equipped": False}).eq(
            "user_id", user.id
        ).execute()

        # 佩戴该徽章
        supabase_admin.table("user_badges").update({"is_equipped": True}).eq(
            "id", user_badge_data["id"]
        ).execute()

        return JsonResponse({"message": "Badge equipped successfully"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def unequip_badge(request, badge_code):
    """
    取消佩戴徽章

    POST /api/reputation/badges/<badge_code>/unequip/
    """
    try:
        user = get_current_user(request)

        # 查找该徽章
        user_badge_result = (
            supabase_admin.table("user_badges")
            .select("id")
            .eq("user_id", user.id)
            .eq("badge_code", badge_code)
            .execute()
        )
        user_badge_data, error = safe_single(
            user_badge_result, "You don't have this badge"
        )
        if error:
            return JsonResponse({"error": error}, status=404)

        # 取消佩戴
        supabase_admin.table("user_badges").update({"is_equipped": False}).eq(
            "id", user_badge_data["id"]
        ).execute()

        return JsonResponse({"message": "Badge unequipped successfully"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
@require_admin
def update_reputation(request):
    """
    更新用户信誉（管理员接口）

    POST /api/reputation/admin/update/
    Body: {
        "user_id": "uuid",
        "score_change": 10,
        "reason": "发布优质内容"
    }
    """
    try:
        try:
            data = parse_json_body(request)
        except ValueError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        target_user_id = data.get("user_id")
        score_change = data.get("score_change", 0)

        if not target_user_id:
            return JsonResponse({"error": "user_id is required"}, status=400)

        # 获取当前信誉
        reputation_result = (
            supabase_admin.table("reputation_summaries")
            .select("*")
            .eq("user_id", target_user_id)
            .execute()
        )
        reputation_data, error = safe_single(reputation_result, "Reputation not found")
        if error:
            return JsonResponse({"error": error}, status=404)

        # 更新分数
        new_score = reputation_data["score"] + score_change

        # 根据分数计算等级
        if new_score < 100:
            level = "novice"
        elif new_score < 500:
            level = "intermediate"
        elif new_score < 1000:
            level = "advanced"
        elif new_score < 5000:
            level = "expert"
        else:
            level = "master"

        # 更新信誉
        result = (
            supabase_admin.table("reputation_summaries")
            .update({"score": new_score, "level": level})
            .eq("user_id", target_user_id)
            .execute()
        )

        return JsonResponse(
            {"message": "Reputation updated successfully", "reputation": result.data[0]}
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
@require_admin
def award_badge(request):
    """
    授予徽章（管理员接口）

    POST /api/reputation/admin/award-badge/
    Body: {
        "user_id": "uuid",
        "badge_code": "first_post"
    }
    """
    try:
        try:
            data = parse_json_body(request)
        except ValueError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        target_user_id = data.get("user_id")
        badge_code = data.get("badge_code")

        if not target_user_id or not badge_code:
            return JsonResponse(
                {"error": "user_id and badge_code are required"}, status=400
            )

        # 检查徽章是否存在
        badge_result = (
            supabase_admin.table("badges").select("*").eq("code", badge_code).execute()
        )
        badge_data, error = safe_single(badge_result, "Badge not found")
        if error:
            return JsonResponse({"error": error}, status=404)

        # 检查用户是否已拥有该徽章
        existing = (
            supabase_admin.table("user_badges")
            .select("id")
            .eq("user_id", target_user_id)
            .eq("badge_code", badge_code)
            .execute()
        )

        if existing.data:
            return JsonResponse({"error": "User already has this badge"}, status=400)

        # 授予徽章
        badge_data = {
            "user_id": target_user_id,
            "badge_code": badge_code,
            "is_equipped": False,
        }

        result = supabase_admin.table("user_badges").insert(badge_data).execute()

        return JsonResponse(
            {"message": "Badge awarded successfully", "user_badge": result.data[0]},
            status=201,
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
