"""
Supabase 辅助函数
提供常用的数据库操作封装
"""


def safe_single(query_result, error_message="Resource not found"):
    """
    安全地获取单条记录

    Args:
        query_result: Supabase 查询结果
        error_message: 未找到记录时的错误消息

    Returns:
        tuple: (data, error)
            - data: 记录数据（如果找到）
            - error: 错误信息（如果未找到）

    Example:
        result = supabase.table("users").select("*").eq("id", user_id).execute()
        data, error = safe_single(result, "User not found")
        if error:
            return JsonResponse({"error": error}, status=404)
        # 使用 data
    """
    if not query_result.data or len(query_result.data) == 0:
        return None, error_message
    return query_result.data[0], None


def get_single_or_none(query_result):
    """
    获取单条记录，如果不存在返回 None（不报错）

    Args:
        query_result: Supabase 查询结果

    Returns:
        dict or None: 记录数据或 None

    Example:
        result = supabase.table("profiles").select("*").eq("id", user_id).execute()
        profile = get_single_or_none(result)
        if not profile:
            # 处理不存在的情况
    """
    if not query_result.data or len(query_result.data) == 0:
        return None
    return query_result.data[0]
