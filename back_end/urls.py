"""
URL configuration for back_end project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework import permissions


class HTTPSSchemaGenerator(OpenAPISchemaGenerator):
    """
    自定义 Schema Generator，强制使用 HTTPS。

    无论请求来自 HTTP 还是 HTTPS，始终生成 HTTPS 的 API 文档。
    这解决了 Nginx 反向代理后 Swagger UI 使用 HTTP 的问题。
    """

    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        # 强制覆盖 schemes 和 host
        schema.schemes = ["https"]
        schema.host = "teentime.cloud"
        return schema


# 创建 openapi.Info，指定 schemes 为 https
api_info = openapi.Info(
    title="Pet Love API",
    default_version="v1",
    description="""
Pet Love 宠物猫粮分析平台 API 文档

## 服务说明

本 API 提供以下核心服务：

### 🤖 AI 报告服务
- LLM 聊天：分析猫粮成分
- 报告管理：保存、查询、删除 AI 报告
- 收藏功能：收藏喜欢的 AI 报告

### 📷 OCR 识别服务
- 图片文字识别：识别猫粮配料表

### 🔍 搜索服务
- 成分信息搜索：查询添加剂和营养成分信息

## 认证说明

大部分接口需要 Supabase JWT 认证：
- 在请求头中添加：`Authorization: Bearer <your_jwt_token>`

## 速率限制

为保护服务资源，所有接口都有速率限制：
- AI 接口：10 次/小时（每用户）
- OCR 接口：20 次/小时（每用户）
- 搜索接口：30 次/小时（每 IP）
""",
    terms_of_service="https://www.example.com/terms/",
    contact=openapi.Contact(email="contact@petlove.com"),
    license=openapi.License(name="MIT License"),
)

# Swagger 文档配置 - 强制使用 HTTPS
schema_view = get_schema_view(
    api_info,
    # 关键：使用 url 参数指定完整的 HTTPS 基础 URL
    url="https://teentime.cloud/",
    public=True,
    permission_classes=[permissions.AllowAny],
    generator_class=HTTPSSchemaGenerator,
)


urlpatterns = [
    # Django Admin（仅用于管理）
    path("admin/", admin.site.urls),
    # 统一 API 路由（所有 API 都通过 api.urls 管理）
    path("api/", include("api.urls")),
    # Swagger 文档
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

# 开发环境提供 media 文件访问
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 生产环境通过 Nginx 提供 media 文件
