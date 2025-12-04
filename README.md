# Pet Love 后端

基于 Django + Supabase 的宠物社区后端服务。

## 项目概述

Pet Love 是一个功能完整的宠物社区平台，提供宠物管理、猫粮评价、论坛互动、AI 分析等功能。

**技术栈：**
- **后端框架**: Django 5.2
- **数据库**: Supabase (PostgreSQL)
- **认证**: Supabase Auth
- **文件存储**: Supabase Storage
- **AI 服务**: OpenAI API
- **OCR**: 阿里云高精版OCR
- **外部 API**: Baidu AppBuilder

---

## 项目结构

```
pet-love-back_end/
├── api/                          # API 视图层
│   ├── auth_views.py             # 认证相关
│   ├── pet_views.py              # 宠物管理
│   ├── catfood_views.py          # 猫粮管理
│   ├── forum_views.py            # 论坛功能
│   ├── comment_views.py          # 评论功能
│   ├── ai_report_views.py        # AI 报告
│   ├── additive_views.py         # 添加剂/成分
│   ├── ocr_views.py              # OCR 识别
│   ├── reputation_views.py       # 信誉系统
│   ├── notification_views.py     # 通知系统
│   ├── tests.py                  # API 测试
│   └── urls.py                   # API 路由
│
├── services/                     # 业务逻辑服务
│   ├── supabase_storage.py       # 文件存储服务
│   └── reputation_service.py     # 信誉系统服务
│
├── utils/                        # 工具函数
│   ├── ocr_utils.py              # OCR 工具
│   └── reputation_utils.py       # 信誉工具
│
├── middleware/                   # Django 中间件
│   └── supabase_auth.py          # Supabase 认证中间件
│
├── config/                       # 配置文件
│   └── supabase_client.py        # Supabase 客户端
│
├── back_end/                     # Django 项目配置
│   ├── settings.py               # 项目设置
│   ├── urls.py                   # URL 配置
│   └── wsgi.py                   # WSGI 配置
│
├── scripts/                      # 数据库脚本
│   ├── supabase_migration.sql    # 数据库迁移脚本
│   ├── add_database_indexes.sql  # 索引优化脚本
│   ├── configure_rls_policies.sql # RLS 策略脚本
│   ├── import_to_supabase.py     # 数据导入脚本
│   ├── export_mysql_data.py      # 数据导出脚本
│   └── setup_supabase_buckets.py # Storage 桶设置脚本
│
├── docs/                         # 文档
│   ├── API_DOCUMENTATION.md      # API 文档
│   └── PROJECT_STRUCTURE_REFACTOR.md # 项目结构说明
│
├── data_export/                  # 导出的数据（备份）
│
├── requirements.txt              # Python 依赖
├── manage.py                     # Django 管理脚本
├── Dockerfile                    # Docker 配置
├── docker-compose.yml            # Docker Compose 配置
└── README.md                     # 项目说明
```

---

## 快速开始

### 1. 环境要求

- Python 3.10+
- Supabase 账号
- OpenAI API Key（可选，用于 AI 分析）
- Baidu AppBuilder API Key（可选，用于成分查询）

### 2. 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd pet-love-back_end

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件：

```env
# Supabase 配置
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key

# OpenAI 配置（用于 AI 分析）
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo

# 阿里云OCR配置（用于图像文字识别）
ALIYUN_OCR_APPCODE=your_aliyun_ocr_appcode
ALIYUN_OCR_URL=https://gjbsb.market.alicloudapi.com/ocrservice/advanced

# Baidu AppBuilder 配置（用于成分查询）
BAIDU_APPBUILDER_API_KEY=your_baidu_api_key

# Django 配置
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 4. 数据库设置

在 Supabase SQL Editor 中依次执行以下脚本：

```bash
# 1. 创建表结构
scripts/supabase_migration.sql

# 2. 添加性能优化索引
scripts/add_database_indexes.sql

# 3. 配置 RLS 安全策略（可选）
scripts/configure_rls_policies.sql
```

### 5. 设置 Supabase Storage

```bash
# 创建存储桶
python scripts/setup_supabase_buckets.py
```

### 6. 运行开发服务器

```bash
# 运行 Django 服务器
python manage.py runserver

# 服务器启动在 http://127.0.0.1:8000
```

---

## API 文档

完整的 API 文档请查看：[docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)

**API 基础 URL**: `http://your-domain.com/api/`

**主要功能模块：**
- 🔐 认证系统 (`/api/auth/`)
- 🐾 宠物管理 (`/api/pets/`)
- 🍖 猫粮管理 (`/api/catfoods/`)
- 💬 论坛系统 (`/api/posts/`)
- 💭 评论系统 (`/api/comments/`)
- 🤖 AI 报告 (`/api/ai/`)
- 🔬 添加剂/成分 (`/api/additive/`)
- 📸 OCR 识别 (`/api/ocr/`)
- ⭐ 信誉系统 (`/api/reputation/`)
- 🔔 通知系统 (`/api/notifications/`)

---

## 数据库架构

### 核心表

| 表名 | 说明 | 关键字段 |
|------|------|----------|
| `profiles` | 用户配置 | username, avatar_url, bio |
| `pets` | 宠物信息 | name, species, breed, age |
| `catfoods` | 猫粮基础信息 | name, brand, score, 营养成分 |
| `catfood_ratings` | 猫粮评分 | catfood_id, user_id, score |
| `catfood_favorites` | 猫粮收藏 | user_id, catfood_id |
| `posts` | 论坛帖子 | author_id, content |
| `comments` | 评论 | target_type, target_id, content |
| `ai_analysis_reports` | AI 分析报告 | catfood_id, ingredients_text |
| `ingredients` | 营养成分 | name, type, label |
| `additives` | 添加剂 | name, en_name, type |
| `reputation_summaries` | 用户信誉 | user_id, score, level |
| `badges` | 徽章定义 | code, name, rule |
| `notifications` | 通知 | recipient_id, verb |

### 数据库特性

- ✅ **Row Level Security (RLS)**: 数据安全保护
- ✅ **自动触发器**: 自动更新时间戳、评分统计
- ✅ **全文搜索**: GIN 索引支持高效搜索
- ✅ **复合索引**: 优化关联查询性能
- ✅ **唯一约束**: 防止重复数据

---

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t pet-love-backend .

# 运行容器
docker run -d -p 8000:8000 --env-file .env pet-love-backend
```

### Docker Compose 部署

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 生产环境配置

1. 设置 `DEBUG=False`
2. 配置 `ALLOWED_HOSTS`
3. 使用环境变量管理敏感信息
4. 配置 HTTPS
5. 设置 CORS 白名单
6. 启用 Supabase RLS 策略

---

## 开发指南

### 添加新的 API 端点

1. 在 `api/` 目录下创建或编辑视图文件
2. 在 `api/urls.py` 中添加路由
3. 使用 `@require_auth` 装饰器保护需要认证的接口
4. 使用 `supabase_admin` 客户端操作数据库

**示例：**

```python
# api/example_views.py
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from middleware.supabase_auth import require_auth
from config.supabase_client import supabase_admin

@require_http_methods(["GET"])
@require_auth
def get_example(request):
    user_id = request.user_id
    
    # 查询数据
    response = supabase_admin.table("table_name").select("*").eq("user_id", user_id).execute()
    
    return JsonResponse({"data": response.data})
```

### 运行测试

```bash
# 运行所有测试
python manage.py test

# 运行特定模块测试
python manage.py test api.tests
```

### 代码规范

- 使用 Black 格式化代码
- 遵循 PEP 8 规范
- 添加必要的注释和文档字符串
- API 返回统一的 JSON 格式

---

## 常见问题

### Q1: 如何导入旧数据？

```bash
# 1. 导出旧数据库数据
python scripts/export_mysql_data.py

# 2. 导入到 Supabase
python scripts/import_to_supabase.py
```

### Q2: 如何重置数据库？

在 Supabase SQL Editor 中：

```sql
-- 删除所有表
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

-- 重新执行迁移脚本
-- 运行 scripts/supabase_migration.sql
```

### Q3: 如何添加管理员用户？

在 Supabase SQL Editor 中：

```sql
UPDATE profiles 
SET is_admin = true 
WHERE email = 'admin@example.com';
```

### Q4: OCR 识别不准确怎么办？

- 确保图片清晰度足够
- 检查 `ALIYUN_OCR_APPCODE` 是否正确配置
- 使用更高分辨率的图片
- 验证阿里云OCR服务配额是否充足

### Q5: AI 分析返回错误？

- 检查 `OPENAI_API_KEY` 是否正确配置
- 确认 API 余额充足
- 查看 `api/ai_report_views.py` 中的错误日志

---

## 性能优化

### 数据库优化

- ✅ 已添加全文搜索索引 (GIN)
- ✅ 已添加复合索引
- ✅ 已添加唯一约束索引
- ✅ 已配置查询优化

### 缓存策略

建议在生产环境中添加：
- Redis 缓存热点数据
- CDN 缓存静态文件
- Supabase Edge Functions 缓存

### 监控建议

- 使用 Supabase Dashboard 监控数据库性能
- 配置慢查询日志
- 监控 API 响应时间
- 设置错误告警

---

## 安全说明

### 已实施的安全措施

- ✅ Supabase Row Level Security (RLS)
- ✅ JWT Token 认证
- ✅ CORS 配置
- ✅ SQL 注入防护（使用 Supabase 客户端）
- ✅ 文件上传验证
- ✅ 敏感信息环境变量管理

### 安全建议

- 定期更新依赖包
- 使用强密码策略
- 启用 HTTPS
- 定期备份数据库
- 监控异常访问

---

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 更新日志

### v2.0.0 (2024-12-04)

**重大更新：**
- ✅ 完全迁移到 Supabase
- ✅ 移除 Django REST Framework
- ✅ 重构项目结构（方案 A）
- ✅ 实现所有核心 API
- ✅ 添加 API 兼容层
- ✅ 优化数据库索引
- ✅ 配置 RLS 安全策略
- ✅ 集成 PaddleOCR
- ✅ 集成 OpenAI API
- ✅ 集成 Baidu AppBuilder API

**删除内容：**
- ❌ Django ORM 模型
- ❌ Django REST Framework
- ❌ Djoser 认证
- ❌ 旧的 app 文件夹结构

---

## 许可证

[MIT License](LICENSE)

---

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。

---

## 致谢

感谢以下开源项目：
- Django
- Supabase
- PaddleOCR
- OpenAI
