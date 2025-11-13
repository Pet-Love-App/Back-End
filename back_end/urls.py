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
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("additive/", include("additive.urls")),
    # 用户认证（注册、登录、JWT）
    path("api/auth/", include("djoser.urls")),
    path("api/auth/", include("djoser.urls.jwt")),
    # 用户资料（头像、宠物）
    path("api/user/", include("user.urls")),
    # AI 报告
    path("api/ai/", include("ai_report.urls")),
    # OCR 识别
    path("ocr/", include("ocr.urls")),
    # 猫粮管理
    path("api/catfood/", include("catfood.urls")),
    # 评论系统
    path("api/comments/", include("comment.urls")),
]

# 开发环境提供 media 文件访问
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 生产环境通过 Nginx 提供 media 文件
