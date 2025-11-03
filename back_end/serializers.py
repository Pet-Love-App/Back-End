"""
Custom serializers with Pydantic validation
集成 Pydantic 验证的 DRF 序列化器
"""

from django.contrib.auth.models import User
from pydantic import ValidationError as PydanticValidationError
from rest_framework import serializers

from .schemas import ChangePasswordSchema, UserRegisterSchema


class PydanticValidationMixin:
    """Pydantic 验证混入类"""

    pydantic_schema = None  # 子类需要指定 Pydantic schema

    def validate(self, attrs):
        """使用 Pydantic 进行验证"""
        if self.pydantic_schema:
            try:
                # 使用 Pydantic 验证数据
                validated_data = self.pydantic_schema(**attrs)

                # 如果有自定义的验证方法，调用它
                if hasattr(validated_data, "validate_password_match"):
                    validated_data.validate_password_match()

                # 将验证后的数据转换回字典
                attrs = validated_data.model_dump()
            except PydanticValidationError as e:
                # 转换 Pydantic 错误为 DRF 错误格式
                errors = {}
                for error in e.errors():
                    field = error["loc"][0] if error["loc"] else "non_field_errors"
                    message = error["msg"]
                    errors[field] = message
                raise serializers.ValidationError(errors)

        return super().validate(attrs)


class CustomUserCreateSerializer(PydanticValidationMixin, serializers.ModelSerializer):
    """自定义用户注册序列化器，集成 Pydantic 验证"""

    pydantic_schema = UserRegisterSchema
    re_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["id", "username", "password", "re_password", "email"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": False},
        }

    def create(self, validated_data):
        """创建用户"""
        # 移除 re_password，因为不需要存储
        validated_data.pop("re_password", None)

        # 使用 create_user 创建用户（会自动加密密码）
        user = User.objects.create_user(**validated_data)
        return user


class CustomSetPasswordSerializer(PydanticValidationMixin, serializers.Serializer):
    """自定义修改密码序列化器，集成 Pydantic 验证"""

    pydantic_schema = ChangePasswordSchema
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    re_new_password = serializers.CharField(write_only=True, required=True)

    def validate_current_password(self, value):
        """验证当前密码是否正确"""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("当前密码不正确")
        return value

    def save(self):
        """保存新密码"""
        user = self.context["request"].user
        password = self.validated_data["new_password"]
        user.set_password(password)
        user.save()
        return user
