"""
宠物相关 API
使用 Supabase 进行数据操作
"""

import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from config.supabase_client import supabase_admin
from middleware.supabase_auth import get_current_user, require_auth
from services.supabase_storage import storage_service


@csrf_exempt
@require_http_methods(["GET"])
@require_auth
def list_pets(request):
    """
    获取当前用户的宠物列表

    GET /api/pets/
    """
    try:
        user = get_current_user(request)

        # 从 Supabase 查询宠物
        result = (
            supabase_admin.table("pets")
            .select("*")
            .eq("user_id", user.id)
            .order("created_at", desc=True)
            .execute()
        )

        return JsonResponse({"pets": result.data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def create_pet(request):
    """
    创建宠物

    POST /api/pets/
    Body: {
        "name": "小白",
        "species": "cat",
        "breed": "英短",
        "age": 2,
        "description": "很可爱"
    }
    """
    try:
        user = get_current_user(request)
        data = json.loads(request.body)

        # 验证必填字段
        if not data.get("name"):
            return JsonResponse({"error": "Pet name is required"}, status=400)

        # 准备数据
        pet_data = {
            "user_id": user.id,
            "name": data.get("name"),
            "species": data.get("species", "cat"),
            "breed": data.get("breed", ""),
            "age": data.get("age"),
            "description": data.get("description", ""),
        }

        # 插入到 Supabase
        result = supabase_admin.table("pets").insert(pet_data).execute()

        return JsonResponse(
            {"message": "Pet created successfully", "pet": result.data[0]}, status=201
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
@require_auth
def update_pet(request, pet_id):
    """
    更新宠物信息

    PUT /api/pets/<pet_id>/
    """
    try:
        user = get_current_user(request)
        data = json.loads(request.body)

        # 验证宠物所有权
        pet = (
            supabase_admin.table("pets")
            .select("*")
            .eq("id", pet_id)
            .eq("user_id", user.id)
            .single()
            .execute()
        )

        if not pet.data:
            return JsonResponse({"error": "Pet not found"}, status=404)

        # 允许更新的字段
        allowed_fields = ["name", "species", "breed", "age", "description"]
        update_data = {k: v for k, v in data.items() if k in allowed_fields}

        if not update_data:
            return JsonResponse({"error": "No valid fields to update"}, status=400)

        # 更新
        result = supabase_admin.table("pets").update(update_data).eq("id", pet_id).execute()

        return JsonResponse({"message": "Pet updated successfully", "pet": result.data[0]})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@require_auth
def delete_pet(request, pet_id):
    """
    删除宠物

    DELETE /api/pets/<pet_id>/
    """
    try:
        user = get_current_user(request)

        # 验证宠物所有权
        pet = (
            supabase_admin.table("pets")
            .select("*")
            .eq("id", pet_id)
            .eq("user_id", user.id)
            .single()
            .execute()
        )

        if not pet.data:
            return JsonResponse({"error": "Pet not found"}, status=404)

        # 删除宠物照片（如果有）
        if pet.data.get("photo_url"):
            storage_service.delete_file_from_url(pet.data["photo_url"])

        # 删除宠物
        supabase_admin.table("pets").delete().eq("id", pet_id).execute()

        return JsonResponse({"message": "Pet deleted successfully"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def upload_pet_photo(request, pet_id):
    """
    上传宠物照片

    POST /api/pets/<pet_id>/photo/
    Body: multipart/form-data with 'photo' file
    """
    try:
        user = get_current_user(request)

        # 验证宠物所有权
        pet = (
            supabase_admin.table("pets")
            .select("*")
            .eq("id", pet_id)
            .eq("user_id", user.id)
            .single()
            .execute()
        )

        if not pet.data:
            return JsonResponse({"error": "Pet not found"}, status=404)

        if "photo" not in request.FILES:
            return JsonResponse({"error": "No photo file provided"}, status=400)

        photo_file = request.FILES["photo"]

        # 检查文件类型
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
        if photo_file.content_type not in allowed_types:
            return JsonResponse(
                {"error": "Invalid file type. Only JPEG, PNG, WEBP allowed"}, status=400
            )

        # 检查文件大小 (5MB)
        if photo_file.size > 5 * 1024 * 1024:
            return JsonResponse({"error": "File too large. Maximum size is 5MB"}, status=400)

        # 上传到 Supabase Storage
        file_extension = photo_file.name.split(".")[-1]
        photo_url = storage_service.upload_pet_photo(
            user.id, pet_id, photo_file.read(), file_extension
        )

        # 更新宠物记录
        supabase_admin.table("pets").update({"photo_url": photo_url}).eq("id", pet_id).execute()

        return JsonResponse({"message": "Photo uploaded successfully", "photo_url": photo_url})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
