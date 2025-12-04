"""
Supabase 认证中间件
验证 JWT token 并将用户信息注入到 request
"""

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from config.supabase_client import supabase


class SupabaseAuthMiddleware(MiddlewareMixin):
    """
    Supabase JWT 认证中间件
    从 Authorization header 中提取 token 并验证
    """

    def process_request(self, request):
        """处理请求，验证 token"""

        # 跳过不需要认证的路径（公开接口）
        exempt_paths = [
            # 认证相关（公开）
            "/api/auth/register/",
            "/api/auth/login/",
            "/api/auth/refresh/",
            "/api/auth/password/reset/",
            "/admin/",
            # 猫粮相关（公开查询）
            "/api/catfoods/",  # GET 列表和详情
            "/api/catfood/by-barcode/",  # 条形码查询
            # 添加剂/成分相关（公开查询）
            "/api/additive/search-additive/",
            "/api/additive/search-ingredient/",
            "/api/search/ingredient/info",
            # 论坛相关（公开查询）
            "/api/posts/",  # GET 列表
            # 评论相关（公开查询）
            "/api/comments/",  # GET 列表
            # 信誉系统（公开查询）
            "/api/reputation/users/",  # 查看其他用户信誉
            "/api/reputation/badges/",  # 徽章列表
            # AI 相关（公开）
            "/api/ai/llm/chat",  # LLM 聊天
            # 通知创建（系统调用）
            "/api/notifications/create/",
        ]

        # 检查是否是豁免路径
        if any(request.path.startswith(path) for path in exempt_paths):
            return None

        # 获取 Authorization header
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if not auth_header:
            # 没有 token，设置匿名用户
            request.supabase_user = None
            return None

        # 提取 token
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                return JsonResponse(
                    {"error": "Invalid authorization scheme"}, status=401
                )
        except ValueError:
            return JsonResponse({"error": "Invalid authorization header"}, status=401)

        # 验证 token
        try:
            user_response = supabase.auth.get_user(token)
            request.supabase_user = user_response.user
            request.supabase_token = token
        except Exception as e:
            return JsonResponse({"error": f"Invalid token: {str(e)}"}, status=401)

        return None


def get_current_user(request):
    """
    从 request 中获取当前用户

    Returns:
        User object 或 None
    """
    return getattr(request, "supabase_user", None)


def require_auth(view_func):
    """
    装饰器：要求用户必须登录

    Usage:
        @require_auth
        def my_view(request):
            user = get_current_user(request)
            ...
    """

    def wrapper(request, *args, **kwargs):
        user = get_current_user(request)
        if not user:
            return JsonResponse({"error": "Authentication required"}, status=401)
        return view_func(request, *args, **kwargs)

    return wrapper


def require_admin(view_func):
    """
    装饰器：要求用户必须是管理员

    Usage:
        @require_admin
        def admin_view(request):
            ...
    """

    def wrapper(request, *args, **kwargs):
        user = get_current_user(request)
        if not user:
            return JsonResponse({"error": "Authentication required"}, status=401)

        # 检查是否是管理员
        try:
            from config.supabase_client import supabase_admin

            profile = (
                supabase_admin.table("profiles")
                .select("is_admin")
                .eq("id", user.id)
                .single()
                .execute()
            )

            if not profile.data or not profile.data.get("is_admin"):
                return JsonResponse({"error": "Admin access required"}, status=403)

        except Exception as e:
            return JsonResponse(
                {"error": f"Failed to verify admin status: {str(e)}"}, status=500
            )

        return view_func(request, *args, **kwargs)

    return wrapper
