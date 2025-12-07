# 🐾 Pet Love - 宠物爱好者社区（后端）

<div align="center">

**基于 Django + Supabase 打造的高性能宠物社区后端服务**

[![Django](https://img.shields.io/badge/Django-5.2-092E20?style=flat&logo=django)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python)](https://www.python.org/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=flat&logo=supabase)](https://supabase.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [API 文档](#-api-文档) • [数据库架构](#-数据库架构) • [部署指南](#-部署指南)

</div>

---

## 📖 项目简介

Pet Love 后端服务是一个功能完整、高性能的 RESTful API 系统，为移动端和 Web 端提供统一的数据接口。采用 Django + Supabase 架构，集成 AI 分析、OCR 识别、社区互动等核心功能。

### ✨ 核心特性

- 🔐 **完整的认证系统** - 基于 Supabase Auth + JWT Token
- 🤖 **AI 智能分析** - 集成 OpenAI GPT 的猫粮配料表深度分析
- 📸 **OCR 文字识别** - 阿里云高精版 OCR，识别准确率 95%+
- 🔬 **成分数据库** - 完整的添加剂和营养成分数据库
- 💬 **社区系统** - 论坛、评论、点赞、收藏功能
- ⭐ **信誉系统** - 用户贡献度评分、等级、徽章
- 🔔 **实时通知** - 基于 Supabase Realtime 的实时通知推送
- 📊 **数据统计** - 用户行为统计、热度排行榜
- 🔒 **安全防护** - Row Level Security (RLS)、速率限制、SQL 注入防护
- 🚀 **高性能** - 数据库索引优化、查询优化、缓存策略

---

## 🏗️ 技术架构

### 核心技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| [Django](https://www.djangoproject.com/) | 5.2+ | Web 框架 |
| [Python](https://www.python.org/) | 3.10+ | 编程语言 |
| [Supabase](https://supabase.com/) | 2.0+ | 后端服务（数据库、认证、存储） |
| [PostgreSQL](https://www.postgresql.org/) | 15+ | 关系型数据库 |
| [Gunicorn](https://gunicorn.org/) | 21.2+ | WSGI 服务器 |
| [Docker](https://www.docker.com/) | 20.10+ | 容器化部署 |

### AI & 外部服务

| 服务 | 用途 |
|------|------|
| [OpenAI API](https://platform.openai.com/) | GPT 模型，猫粮配料表智能分析 |
| [阿里云 OCR](https://market.aliyun.com/) | 高精版文字识别 |
| [Baidu AppBuilder](https://console.bce.baidu.com/) | 成分百科信息查询 |

### 功能模块

- 🔐 **认证模块** - 注册、登录、令牌刷新、邮箱验证
- 🐾 **宠物管理** - CRUD、图片上传、多宠物关联
- 🍖 **猫粮管理** - CRUD、评分、收藏、营养成分分析
- 💬 **论坛系统** - 帖子发布、编辑、删除、点赞
- 💭 **评论系统** - 多级评论、回复、点赞
- 🤖 **AI 报告** - 配料表分析、营养成分占比、安全性评估
- 🔬 **成分数据库** - 添加剂、营养成分查询
- 📸 **OCR 识别** - 图片文字提取、配料表识别
- ⭐ **信誉系统** - 积分、等级、徽章、贡献度排行
- 🔔 **通知系统** - 评论通知、点赞通知、系统通知

---

## 🚀 快速开始

### 📋 前置要求

在开始之前，请确保你的开发环境已安装：

- **Python** >= 3.10 ([下载](https://www.python.org/downloads/))
- **pip** >= 21.0
- **Supabase 账号** ([注册](https://supabase.com/))
- **Docker** (可选，用于容器化部署)

### 📥 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/Pet-Love-App/Back-End.git
cd pet-love-back_end

# 2. 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt
```

### ⚙️ 环境配置

创建 `.env` 文件：

```env
# ==================== Django 配置 ====================
SECRET_KEY=your_django_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# ==================== Supabase 配置 ====================
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key

# ==================== OpenAI 配置（AI 分析） ====================
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo

# ==================== 阿里云 OCR 配置 ====================
ALIYUN_OCR_APPCODE=your_aliyun_ocr_appcode
ALIYUN_OCR_URL=https://gjbsb.market.alicloudapi.com/ocrservice/advanced

# ==================== Baidu AppBuilder 配置 ====================
BAIDU_APPBUILDER_API_KEY=your_baidu_api_key

# ==================== CORS 配置（可选） ====================
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:19006
```

## 📂 项目结构

```
pet-love-back_end/
├── api/                              # API 视图层
│   ├── auth_views.py                 # 🔐 认证相关（登录、注册、登出）
│   ├── pet_views.py                  # 🐾 宠物管理（CRUD）
│   ├── catfood_views.py              # 🍖 猫粮管理（CRUD、评分、收藏）
│   ├── forum_views.py                # 💬 论坛功能（帖子、点赞）
│   ├── comment_views.py              # 💭 评论功能（发布、回复、删除）
│   ├── ai_report_views.py            # 🤖 AI 报告（生成、保存、查询）
│   ├── additive_views.py             # 🔬 添加剂/成分查询
│   ├── ocr_views.py                  # 📸 OCR 识别
│   ├── search_views.py               # 🔍 搜索功能（百度百科）
│   ├── reputation_views.py           # ⭐ 信誉系统（积分、等级、徽章）
│   ├── notification_views.py         # 🔔 通知系统
│   ├── tests.py                      # 🧪 API 测试
│   └── urls.py                       # 🛣️ API 路由配置
│
├── services/                         # 业务逻辑服务层
│   ├── ocr_service.py                # OCR 识别服务（阿里云 API 封装）
│   ├── ai_service.py                 # AI 分析服务（OpenAI API 封装）
│   ├── search_service.py             # 搜索服务（百度百科 API 封装）
│   ├── supabase_storage.py           # 文件存储服务（Supabase Storage）
│   └── reputation_service.py         # 信誉系统服务（积分计算、等级升级）
│
├── middleware/                       # Django 中间件
│   └── supabase_auth.py              # Supabase JWT 认证中间件
│
├── config/                           # 配置文件
│   └── supabase_client.py            # Supabase 客户端初始化
│
├── back_end/                         # Django 项目配置
│   ├── settings.py                   # 项目设置（数据库、中间件、CORS等）
│   ├── urls.py                       # 根 URL 配置
│   └── wsgi.py                       # WSGI 应用入口
│
├── scripts/                          # 数据库脚本和工具
│   ├── supabase_migration.sql        # 📊 数据库表结构迁移脚本
│   ├── add_database_indexes.sql      # 🚀 性能优化索引脚本
│   ├── configure_rls_policies.sql    # 🔒 RLS 安全策略脚本
│   ├── import_to_supabase.py         # 🔄 数据导入脚本
│   ├── export_mysql_data.py          # 📤 数据导出脚本（从旧系统迁移）
│   └── setup_supabase_buckets.py     # 🗂️ Storage 桶设置脚本
│
├── docs/                             # 文档
│   ├── API_DOCUMENTATION.md          # 📖 API 接口文档
│   └── PROJECT_STRUCTURE_REFACTOR.md # 🏗️ 项目结构重构说明
│
├── data_export/                      # 数据导出目录（备份）
│   └── (导出的 JSON 数据文件)
│
├── .env                              # ⚙️ 环境变量配置（不提交到 Git）
├── .env.example                      # 📝 环境变量示例文件
├── requirements.txt                  # 📦 Python 依赖
├── manage.py                         # 🔧 Django 管理脚本
├── Dockerfile                        # 🐳 Docker 镜像构建文件
├── docker-compose.yml                # 🐳 Docker Compose 编排文件
└── README.md                         # 📄 项目说明文档
```

### 主要 API 端点

| 模块 | 端点 | 说明 |
|------|------|------|
| 🔐 **认证** | `/api/auth/` | 注册、登录、登出、令牌刷新 |
| 🐾 **宠物** | `/api/pets/` | 宠物 CRUD、图片上传 |
| 🍖 **猫粮** | `/api/catfoods/` | 猫粮 CRUD、评分、收藏、搜索 |
| 💬 **论坛** | `/api/posts/` | 帖子发布、编辑、删除、点赞 |
| 💭 **评论** | `/api/comments/` | 评论发布、回复、删除、点赞 |
| 🤖 **AI 报告** | `/api/ai/` | 生成报告、保存报告、查询报告 |
| 🔬 **成分** | `/api/additive/` | 添加剂/成分查询 |
| 📸 **OCR** | `/api/ocr/` | 图片文字识别 |
| 🔍 **搜索** | `/api/search/` | 百度百科搜索 |
| ⭐ **信誉** | `/api/reputation/` | 用户积分、等级、徽章 |
| 🔔 **通知** | `/api/notifications/` | 通知列表、标记已读 |

---

## 🗄️ 数据库架构

### 核心数据表

| 表名 | 说明 | 关键字段 |
|------|------|----------|
| `profiles` | 用户资料 | username, avatar_url, bio, is_admin |
| `pets` | 宠物信息 | name, species, breed, age, owner_id |
| `catfoods` | 猫粮基础信息 | name, brand, score, 营养成分占比 |
| `catfood_ratings` | 猫粮评分 | catfood_id, user_id, score, review |
| `catfood_favorites` | 猫粮收藏 | user_id, catfood_id |
| `posts` | 论坛帖子 | author_id, content, likes_count |
| `comments` | 评论 | target_type, target_id, content, parent_id |
| `ai_analysis_reports` | AI 分析报告 | catfood_id, ingredients_text, analysis |
| `ingredients` | 营养成分库 | name, type, label, description |
| `additives` | 添加剂库 | name, en_name, type, safety_level |
| `reputation_summaries` | 用户信誉 | user_id, score, level, badges |
| `badges` | 徽章定义 | code, name, icon, rule |
| `notifications` | 通知 | recipient_id, actor_id, verb, target |

### 数据库特性

- ✅ **Row Level Security (RLS)** - 数据隔离，防止越权访问
- ✅ **自动触发器** - 自动更新时间戳、统计数据
- ✅ **全文搜索 (GIN 索引)** - 高效的中文全文搜索
- ✅ **复合索引** - 优化关联查询性能
- ✅ **唯一约束** - 防止重复数据（用户名、邮箱等）
- ✅ **外键约束** - 保证数据一致性
- ✅ **级联删除** - 自动清理关联数据

### ER 图（简化版）

```
profiles (用户)
    ↓
    ├─ pets (宠物)
    ├─ catfood_ratings (评分)
    ├─ catfood_favorites (收藏)
    ├─ posts (帖子)
    ├─ comments (评论)
    └─ reputation_summaries (信誉)

catfoods (猫粮)
    ↓
    ├─ ai_analysis_reports (AI 报告)
    ├─ catfood_ratings (评分)
    └─ catfood_favorites (收藏)
```

## ⚡ 性能优化

### 已实施的优化

- ✅ **数据库索引** - 全文搜索索引、复合索引、唯一索引
- ✅ **查询优化** - 减少 N+1 查询、使用 select 指定字段
- ✅ **连接池** - Supabase 内置连接池
- ✅ **CDN 加速** - Supabase Storage 自带 CDN
