"""
统一配置管理
使用 Pydantic 进行类型安全的配置管理
"""

import json

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# 默认允许的主机列表，供默认值和解析兜底使用
DEFAULT_ALLOWED_HOSTS = ["82.157.255.92", "localhost", "127.0.0.1", "*"]


class Settings(BaseSettings):
    """应用配置"""

    # ==================== Supabase 配置 ====================
    SUPABASE_URL: str = Field(default="", description="Supabase 项目 URL")
    SUPABASE_ANON_KEY: str = Field(default="", description="Supabase 匿名密钥")
    SUPABASE_SERVICE_KEY: str = Field(default="", description="Supabase 服务密钥")

    # ==================== AI 服务配置 ====================
    LLM_API_KEY: str = Field(default="", description="LLM API 密钥")
    LLM_API_URL: str = Field(
        default="https://llmapi.paratera.com/v1/chat/completions",
        description="LLM API 地址",
    )
    LLM_MODEL: str = Field(default="DeepSeek-V3.2-Exp", description="LLM 模型名称")

    # ==================== OCR 服务配置 ====================
    ALIYUN_OCR_APPCODE: str = Field(default="", description="阿里云 OCR AppCode")
    ALIYUN_OCR_URL: str = Field(
        default="https://gjbsb.market.alicloudapi.com/ocrservice/advanced",
        description="阿里云 OCR API 地址",
    )

    # ==================== 搜索服务配置 ====================
    BAIDU_API_KEY: str = Field(default="", description="百度 API 密钥")
    BAIDU_APP_ID: str = Field(default="", description="百度 App ID")

    # ==================== Django 配置 ====================
    SECRET_KEY: str = Field(
        default="django-insecure-8l#yd#zg_xlp4x08h9rtmow_0j%3=2))5t1^h_75bjhp7ez1s!",
        description="Django 密钥",
    )
    DEBUG: bool = Field(default=True, description="调试模式")
    # 允许字符串或列表输入，避免空字符串触发 json 解析错误
    ALLOWED_HOSTS: list[str] | str = Field(
        default_factory=lambda: DEFAULT_ALLOWED_HOSTS.copy(), description="允许的主机"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # 忽略额外的环境变量
    )

    # ==================== 配置验证方法 ====================

    def is_supabase_configured(self) -> bool:
        """检查 Supabase 是否配置"""
        return bool(self.SUPABASE_URL and self.SUPABASE_SERVICE_KEY)

    def is_ai_configured(self) -> bool:
        """检查 AI 服务是否配置"""
        return bool(self.LLM_API_KEY)

    def is_ocr_configured(self) -> bool:
        """检查 OCR 服务是否配置"""
        return bool(self.ALIYUN_OCR_APPCODE)

    def is_search_configured(self) -> bool:
        """检查搜索服务是否配置"""
        return bool(self.BAIDU_API_KEY)

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, value: str | list[str] | None) -> list[str] | None:
        """
        兼容多种 ALLOWED_HOSTS 配置方式：
        - 空值或空字符串：回退到默认列表，避免 json 解析错误
        - JSON 字符串：优先尝试 json.loads
        - 逗号分隔字符串：例如 "a.com,b.com"
        """
        if value in (None, "", "[]"):
            return DEFAULT_ALLOWED_HOSTS.copy()
        if isinstance(value, str):
            trimmed = value.strip()
            if not trimmed:
                return DEFAULT_ALLOWED_HOSTS.copy()
            try:
                parsed = json.loads(trimmed)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass
            return [host.strip() for host in trimmed.split(",") if host.strip()]
        return value


# 全局配置实例
settings = Settings()

# 向后兼容：导出常用配置
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_ANON_KEY = settings.SUPABASE_ANON_KEY
SUPABASE_SERVICE_KEY = settings.SUPABASE_SERVICE_KEY
