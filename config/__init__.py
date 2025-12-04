"""配置模块"""

from .supabase_client import get_supabase_client, supabase, supabase_admin

__all__ = ["get_supabase_client", "supabase", "supabase_admin"]
