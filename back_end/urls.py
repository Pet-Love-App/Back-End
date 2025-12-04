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
from django.http import JsonResponse
from django.urls import include, path


def health_check(request):
    """健康检查端点 - 用于 Docker 健康检查和负载均衡"""
    return JsonResponse({"status": "ok", "service": "Pet Love Backend"})


urlpatterns = [
    # 健康检查端点
    path("health/", health_check, name="health_check"),
    # Django Admin（仅用于管理）
    path("admin/", admin.site.urls),
    # 统一 API 路由（所有 API 都通过 api.urls 管理）
    path("api/", include("api.urls")),
]

# 开发环境提供 media 文件访问
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 生产环境通过 Nginx 提供 media 文件
