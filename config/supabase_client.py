"""
Supabase 客户端配置
提供统一的 Supabase 连接实例
"""

import os
from typing import Optional

from supabase import Client, create_client

# 从环境变量读取配置
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")


class SupabaseClient:
    """Supabase 客户端单例"""

    _instance: Client | None = None
    _service_instance: Client | None = None

    @classmethod
    def get_client(cls, use_service_key: bool = False) -> Client:
        """
        获取 Supabase 客户端实例

        Args:
            use_service_key: 是否使用 service_role key (绕过 RLS)

        Returns:
            Supabase Client 实例
        """
        if not SUPABASE_URL:
            raise ValueError("SUPABASE_URL 未配置，请检查环境变量")

        if use_service_key:
            if not SUPABASE_SERVICE_KEY:
                raise ValueError("SUPABASE_SERVICE_KEY 未配置，请检查环境变量")

            if cls._service_instance is None:
                cls._service_instance = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
            return cls._service_instance
        else:
            if not SUPABASE_ANON_KEY:
                raise ValueError("SUPABASE_ANON_KEY 未配置，请检查环境变量")

            if cls._instance is None:
                cls._instance = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            return cls._instance


# 便捷函数
def get_supabase_client(use_service_key: bool = False) -> Client:
    """获取 Supabase 客户端"""
    return SupabaseClient.get_client(use_service_key)


# 默认客户端实例（使用 anon key）
supabase = get_supabase_client()

# Service role 客户端实例（绕过 RLS，用于管理操作）
supabase_admin = get_supabase_client(use_service_key=True)
