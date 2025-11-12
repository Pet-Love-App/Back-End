# 快速开始指南

## 快速部署和测试

### 1. 运行数据库迁移

```bash
cd E:\Desktop\back_end

# 创建迁移文件
python manage.py makemigrations catfood
python manage.py makemigrations comment

# 应用迁移
python manage.py migrate
```

### 2. 启动开发服务器

```bash
python manage.py runserver
```

服务器将在 `http://127.0.0.1:8000` 启动。

### 3. 快速测试 API

#### 测试 1: 获取猫粮列表

```bash
curl http://127.0.0.1:8000/api/catfood/
```

#### 测试 2: 创建猫粮（需要 POST）

```bash
curl -X POST http://127.0.0.1:8000/api/catfood/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试猫粮",
    "brand": "测试品牌",
    "desc": "这是一个测试猫粮",
    "percentage": true,
    "percentData": {
      "crude_protein": 44.0,
      "crude_fat": 20.0,
      "crude_fiber": 1.8,
      "crude_ash": 8.7,
      "others": 10.0
    },
    "tags": ["成猫粮", "高蛋白"],
    "nutrition": [],
    "additive": [],
    "safety": "安全性良好",
    "nutrient": "营养均衡"
  }'
```

#### 测试 3: 搜索猫粮

```bash
curl "http://127.0.0.1:8000/api/catfood/search/?name=测试"
```

#### 测试 4: 获取评论列表

```bash
curl http://127.0.0.1:8000/api/comments/
```

#### 测试 5: 创建评论（需要登录）

首先获取 JWT Token：

```bash
# 创建用户（如果还没有）
curl -X POST http://127.0.0.1:8000/api/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123",
    "re_password": "testpass123"
  }'

# 登录获取 token
curl -X POST http://127.0.0.1:8000/api/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

然后使用 token 创建评论：

```bash
curl -X POST http://127.0.0.1:8000/api/comments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "content": "这个猫粮很不错！",
    "targetId": 1,
    "targetType": "catfood"
  }'
```

#### 测试 6: 点赞评论

```bash
curl -X POST http://127.0.0.1:8000/api/comments/1/like/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. 使用 Django Admin 管理数据

创建超级用户：

```bash
python manage.py createsuperuser
```

然后访问 `http://127.0.0.1:8000/admin/` 登录后可以管理所有数据。

## API 端点速查表

### 猫粮 API
- `GET /api/catfood/` - 获取列表
- `POST /api/catfood/` - 创建猫粮
- `GET /api/catfood/{id}/` - 获取详情
- `PUT /api/catfood/{id}/` - 更新猫粮
- `PATCH /api/catfood/{id}/` - 部分更新
- `DELETE /api/catfood/{id}/` - 删除猫粮
- `GET /api/catfood/search/?name=xxx` - 搜索猫粮
- `GET /api/catfood/{id}/comments/` - 获取评论

### 评论 API
- `GET /api/comments/` - 获取列表
- `POST /api/comments/` - 创建评论 🔐
- `GET /api/comments/{id}/` - 获取详情
- `PUT /api/comments/{id}/` - 更新评论 🔐
- `DELETE /api/comments/{id}/` - 删除评论 🔐
- `POST /api/comments/{id}/like/` - 点赞/取消点赞 🔐

🔐 = 需要认证

## 常见问题

### Q: 如何获取 JWT Token？

A: 使用以下 API：
- 注册: `POST /api/auth/users/`
- 登录: `POST /api/auth/jwt/create/`
- 刷新: `POST /api/auth/jwt/refresh/`

### Q: 如何在请求中使用 Token？

A: 在请求头中添加：
```
Authorization: Bearer {your_access_token}
```

### Q: 数据库用 MySQL 还是 SQLite？

A: 默认使用 MySQL。如果要使用 SQLite，设置环境变量：
```bash
export USE_SQLITE=True
```

### Q: 如何查看所有可用的 API？

A: 访问：
- REST Framework 浏览界面: `http://127.0.0.1:8000/api/catfood/`
- 或查看文档: `docs/API_CATFOOD_COMMENT.md`

## 更多信息

- 📚 完整 API 文档: `docs/API_CATFOOD_COMMENT.md`
- 🗄️ 数据库设置: `docs/DATABASE_SETUP.md`
- 📝 实现总结: `docs/IMPLEMENTATION_SUMMARY.md`

## 前端集成

在前端项目中，可以这样使用 API：

```typescript
// 获取猫粮列表
const response = await fetch('http://127.0.0.1:8000/api/catfood/');
const catfoods = await response.json();

// 搜索猫粮
const searchResponse = await fetch('http://127.0.0.1:8000/api/catfood/search/?name=皇家');
const results = await searchResponse.json();

// 创建评论（需要 token）
const createComment = await fetch('http://127.0.0.1:8000/api/comments/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    content: '很不错！',
    targetId: 1,
    targetType: 'catfood'
  })
});
```

## 完成！

现在你可以开始使用这些 API 了。如有问题，请查看相关文档或联系开发团队。

