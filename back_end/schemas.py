"""
Pydantic schemas for data validation
用于请求和响应的数据验证模型
"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class UserRegisterSchema(BaseModel):
    """用户注册验证"""

    username: str = Field(..., min_length=3, max_length=150, description="用户名")
    password: str = Field(..., min_length=6, description="密码")
    re_password: str = Field(..., min_length=6, description="确认密码")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """验证用户名格式"""
        if not v.replace("_", "").isalnum():
            raise ValueError("用户名只能包含字母、数字和下划线")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """验证密码强度"""
        if not any(c.isalpha() for c in v):
            raise ValueError("密码必须包含字母")
        if not any(c.isdigit() for c in v):
            raise ValueError("密码必须包含数字")
        return v

    def validate_password_match(self) -> "UserRegisterSchema":
        """验证两次密码是否一致"""
        if self.password != self.re_password:
            raise ValueError("两次输入的密码不一致")
        return self


class UserLoginSchema(BaseModel):
    """用户登录验证"""

    username: str = Field(..., min_length=3, max_length=150, description="用户名")
    password: str = Field(..., min_length=1, description="密码")


class ChangePasswordSchema(BaseModel):
    """修改密码验证"""

    current_password: str = Field(..., min_length=1, description="当前密码")
    new_password: str = Field(..., min_length=6, description="新密码")
    re_new_password: str = Field(..., min_length=6, description="确认新密码")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """验证新密码强度"""
        if not any(c.isalpha() for c in v):
            raise ValueError("密码必须包含字母")
        if not any(c.isdigit() for c in v):
            raise ValueError("密码必须包含数字")
        return v

    def validate_password_match(self) -> "ChangePasswordSchema":
        """验证两次新密码是否一致"""
        if self.new_password != self.re_new_password:
            raise ValueError("两次输入的新密码不一致")
        return self


class UserResponseSchema(BaseModel):
    """用户信息响应"""

    id: int
    username: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None

    class Config:
        from_attributes = True  # 允许从 ORM 对象创建
