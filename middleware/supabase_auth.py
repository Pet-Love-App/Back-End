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
        import re

        # 完全公开的路径（任何方法都不需要认证）
        public_paths = [
            # 认证相关
            "/api/auth/register/",
            "/api/auth/login/",
            "/api/auth/refresh/",
            "/api/auth/password/reset/",
            "/admin/",
            # 添加剂/成分相关
            "/api/additive/search-additive/",
            "/api/additive/search-ingredient/",
            "/api/search/ingredient/info",
            # 条形码查询
            "/api/catfood/by-barcode/",
            # AI LLM 聊天
            "/api/ai/llm/chat",
            # 通知创建（系统调用）
            "/api/notifications/create/",
        ]

        # 仅 GET 方法公开的路径（使用正则表达式）
        public_get_patterns = [
            r"^/api/catfoods/$",  # 猫粮列表
            r"^/api/catfoods/\d+/$",  # 猫粮详情
            r"^/api/catfoods/\d+/ratings/$",  # 猫粮评分列表
            r"^/api/catfood/likes/count/\d+/$",  # 猫粮点赞数
            r"^/api/catfood/\d+/comments/$",  # 猫粮评论列表
            r"^/api/posts/$",  # 论坛列表
            r"^/api/comments/$",  # 评论列表
            r"^/api/reputation/users/[\w-]+/$",  # 查看用户信誉
            r"^/api/reputation/badges/$",  # 徽章列表
        ]

        # 检查完全公开的路径
        for path in public_paths:
            if request.path.startswith(path):
                return None

        # 检查仅 GET 公开的路径
        if request.method == "GET":
            for pattern in public_get_patterns:
                if re.match(pattern, request.path):
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
