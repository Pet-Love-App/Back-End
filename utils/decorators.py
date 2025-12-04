from functools import wraps

from django.http import JsonResponse

from config.supabase_client import supabase_admin
from middleware.supabase_auth import get_current_user


def require_admin(view_func):
    """
    装饰器：要求用户具有管理员权限
    必须在 @require_auth 之后使用
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            user = get_current_user(request)
            if not user:
                return JsonResponse({"error": "Authentication required"}, status=401)

            # 检查管理员权限
            response = (
                supabase_admin.table("profiles")
                .select("is_admin")
                .eq("id", user.id)
                .execute()
            )

            # 安全地检查结果
            is_admin = False
            if response.data and len(response.data) > 0:
                is_admin = response.data[0].get("is_admin", False)

            if not is_admin:
                return JsonResponse({"error": "Admin permission required"}, status=403)

            return view_func(request, *args, **kwargs)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return _wrapped_view
