"""
认证相关 API
处理登录、注册、密码重置等
"""

import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from config.supabase_client import supabase, supabase_admin
from middleware.supabase_auth import get_current_user, require_auth


@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    """
    用户注册

    POST /api/auth/register/
    Body: {
        "email": "user@example.com",
        "password": "password123",
        "username": "username"
    }
    """
    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")
        username = data.get("username")

        if not email or not password or not username:
            return JsonResponse(
                {"error": "Email, password and username are required"}, status=400
            )

        # 检查用户名是否已存在
        try:
            existing_profile = (
                supabase_admin.table("profiles")
                .select("id")
                .eq("username", username)
                .execute()
            )
            if existing_profile.data:
                return JsonResponse({"error": "Username already exists"}, status=400)
        except Exception as check_error:
            # 如果查询失败，记录错误但继续注册流程
            print(f"Username check error: {check_error}")

        # 使用 Supabase Auth 注册
        auth_response = supabase.auth.sign_up(
            {
                "email": email,
                "password": password,
                "options": {"data": {"username": username}},
            }
        )

        if not auth_response.user:
            return JsonResponse({"error": "Registration failed"}, status=400)

        # 创建 profile
        profile_data = {
            "id": auth_response.user.id,
            "username": username,
            "bio": "",
            "is_admin": False,
        }

        try:
            supabase_admin.table("profiles").insert(profile_data).execute()
        except Exception as profile_error:
            print(f"Profile creation error: {profile_error}")
            # Profile 创建失败不影响注册

        # 创建信誉记录
        reputation_data = {
            "user_id": auth_response.user.id,
            "score": 0,
            "level": "novice",
        }

        try:
            supabase_admin.table("reputation_summaries").insert(
                reputation_data
            ).execute()
        except Exception as rep_error:
            print(f"Reputation creation error: {rep_error}")
            # 信誉记录创建失败不影响注册

        return JsonResponse(
            {
                "message": "Registration successful",
                "user": {
                    "id": auth_response.user.id,
                    "email": auth_response.user.email,
                    "username": username,
                },
                "session": {
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,
                },
            },
            status=201,
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        import traceback

        error_detail = traceback.format_exc()
        print(f"Registration error: {error_detail}")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    """
    用户登录

    POST /api/auth/login/
    Body: {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return JsonResponse(
                {"error": "Email and password are required"}, status=400
            )

        # 使用 Supabase Auth 登录
        auth_response = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )

        if not auth_response.user:
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        # 获取用户 profile
        profile = (
            supabase_admin.table("profiles")
            .select("*")
            .eq("id", auth_response.user.id)
            .single()
            .execute()
        )

        return JsonResponse(
            {
                "message": "Login successful",
                "user": {
                    "id": auth_response.user.id,
                    "email": auth_response.user.email,
                    "username": profile.data.get("username") if profile.data else None,
                    "avatar_url": profile.data.get("avatar_url")
                    if profile.data
                    else None,
                    "is_admin": profile.data.get("is_admin", False)
                    if profile.data
                    else False,
                },
                "session": {
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,
                },
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def logout(request):
    """
    用户登出

    POST /api/auth/logout/
    """
    try:
        # Supabase 客户端登出
        supabase.auth.sign_out()

        return JsonResponse({"message": "Logout successful"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@require_auth
def get_profile(request):
    """
    获取当前用户信息

    GET /api/auth/profile/
    """
    try:
        user = get_current_user(request)

        # 获取完整的 profile 信息
        profile = (
            supabase_admin.table("profiles")
            .select("*")
            .eq("id", user.id)
            .single()
            .execute()
        )

        # 获取信誉信息
        reputation = (
            supabase_admin.table("reputation_summaries")
            .select("*")
            .eq("user_id", user.id)
            .single()
            .execute()
        )

        # 获取徽章
        badges = (
            supabase_admin.table("user_badges")
            .select("*, badge:badges(*)")
            .eq("user_id", user.id)
            .execute()
        )

        return JsonResponse(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    **profile.data,
                },
                "reputation": reputation.data if reputation.data else None,
                "badges": badges.data if badges.data else [],
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
@require_auth
def update_profile(request):
    """
    更新用户信息

    PUT /api/auth/profile/
    Body: {
        "username": "new_username",
        "bio": "new bio",
        "phone": "1234567890"
    }
    """
    try:
        user = get_current_user(request)
        data = json.loads(request.body)

        # 允许更新的字段
        allowed_fields = ["username", "bio", "phone"]
        update_data = {k: v for k, v in data.items() if k in allowed_fields}

        if not update_data:
            return JsonResponse({"error": "No valid fields to update"}, status=400)

        # 如果更新用户名，检查是否已存在
        if "username" in update_data:
            existing = (
                supabase_admin.table("profiles")
                .select("id")
                .eq("username", update_data["username"])
                .neq("id", user.id)
                .execute()
            )

            if existing.data:
                return JsonResponse({"error": "Username already exists"}, status=400)

        # 更新 profile
        result = (
            supabase_admin.table("profiles")
            .update(update_data)
            .eq("id", user.id)
            .execute()
        )

        return JsonResponse(
            {"message": "Profile updated successfully", "profile": result.data[0]}
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def upload_avatar(request):
    """
    上传头像

    POST /api/auth/avatar/
    Body: multipart/form-data with 'avatar' file
    """
    try:
        user = get_current_user(request)

        if "avatar" not in request.FILES:
            return JsonResponse({"error": "No avatar file provided"}, status=400)

        avatar_file = request.FILES["avatar"]

        # 检查文件类型
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
        if avatar_file.content_type not in allowed_types:
            return JsonResponse(
                {"error": "Invalid file type. Only JPEG, PNG, WEBP allowed"}, status=400
            )

        # 检查文件大小 (5MB)
        if avatar_file.size > 5 * 1024 * 1024:
            return JsonResponse(
                {"error": "File too large. Maximum size is 5MB"}, status=400
            )

        # 上传到 Supabase Storage
        from services.supabase_storage import storage_service

        file_extension = avatar_file.name.split(".")[-1]
        avatar_url = storage_service.upload_avatar(
            user.id, avatar_file.read(), file_extension
        )

        # 更新 profile
        supabase_admin.table("profiles").update({"avatar_url": avatar_url}).eq(
            "id", user.id
        ).execute()

        return JsonResponse(
            {"message": "Avatar uploaded successfully", "avatar_url": avatar_url}
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@require_auth
def delete_avatar(request):
    """
    删除头像

    DELETE /api/auth/avatar/
    """
    try:
        user = get_current_user(request)

        # 获取当前头像 URL
        profile = (
            supabase_admin.table("profiles")
            .select("avatar_url")
            .eq("id", user.id)
            .single()
            .execute()
        )

        if profile.data and profile.data.get("avatar_url"):
            # 删除 Storage 中的文件
            from services.supabase_storage import storage_service

            file_path = storage_service.extract_file_path_from_url(
                profile.data["avatar_url"], storage_service.BUCKETS["avatars"]
            )
            if file_path:
                storage_service.delete_file(
                    storage_service.BUCKETS["avatars"], file_path
                )

        # 更新 profile，清空头像 URL
        supabase_admin.table("profiles").update({"avatar_url": None}).eq(
            "id", user.id
        ).execute()

        return JsonResponse({"message": "Avatar deleted successfully"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def change_password(request):
    """
    修改密码

    POST /api/auth/password/change/
    Body: {
        "old_password": "old_password",
        "new_password": "new_password"
    }
    """
    try:
        user = get_current_user(request)
        data = json.loads(request.body)

        old_password = data.get("old_password")
        new_password = data.get("new_password")

        if not old_password or not new_password:
            return JsonResponse(
                {"error": "Old password and new password are required"}, status=400
            )

        # 验证新密码强度
        if len(new_password) < 6:
            return JsonResponse(
                {"error": "New password must be at least 6 characters"}, status=400
            )

        # 验证旧密码（通过重新登录）
        try:
            supabase.auth.sign_in_with_password(
                {"email": user.email, "password": old_password}
            )
        except Exception:
            return JsonResponse({"error": "Old password is incorrect"}, status=400)

        # 更新密码
        supabase.auth.update_user({"password": new_password})

        return JsonResponse({"message": "Password changed successfully"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def reset_password_request(request):
    """
    请求重置密码（发送重置邮件）

    POST /api/auth/password/reset/
    Body: {
        "email": "user@example.com"
    }
    """
    try:
        data = json.loads(request.body)
        email = data.get("email")

        if not email:
            return JsonResponse({"error": "Email is required"}, status=400)

        # 发送密码重置邮件
        supabase.auth.reset_password_email(email)

        return JsonResponse({"message": "Password reset email sent successfully"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def refresh_token(request):
    """
    刷新访问令牌

    POST /api/auth/refresh/
    Body: {
        "refresh_token": "xxx"
    }
    """
    try:
        data = json.loads(request.body)
        refresh_token = data.get("refresh_token")

        if not refresh_token:
            return JsonResponse({"error": "Refresh token is required"}, status=400)

        # 刷新 token
        auth_response = supabase.auth.refresh_session(refresh_token)

        return JsonResponse(
            {
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token,
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
