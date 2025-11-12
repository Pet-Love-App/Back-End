# 猫粮和评论 API 文档

## 基础信息

- 基础路径: `http://your-server/api`
- 认证方式: JWT Token（部分接口需要认证）
- Content-Type: `application/json`

## 猫粮 API

### 1. 获取猫粮列表

**请求**
```
GET /api/catfood/
```

**响应示例**
```json
[
  {
    "id": 1,
    "name": "皇家猫粮",
    "brand": "Royal Canin",
    "desc": "适合成年猫的营养猫粮",
    "score": 4.5,
    "countNum": 100,
    "imageUrl": "http://example.com/image.jpg",
    "tags": [
      {"id": 1, "name": "成猫粮"},
      {"id": 2, "name": "高蛋白"}
    ],
    "nutrition": [
      {"id": 1, "name": "鸡肉", "type": "蛋白质", "label": "优质", "desc": "..."}
    ],
    "additive": [
      {"id": 1, "name": "牛磺酸", "en_name": "Taurine", "applicable_range": "猫粮", "type": "营养强化剂"}
    ],
    "safety": "安全性分析内容...",
    "nutrient": "营养分析内容...",
    "percentage": true,
    "percentData": {
      "crude_protein": 44.0,
      "crude_fat": 20.0,
      "carbohydrates": null,
      "crude_fiber": 1.8,
      "crude_ash": 8.7,
      "others": 10.0
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### 2. 获取单个猫粮详情

**请求**
```
GET /api/catfood/{id}/
```

**响应**: 与列表中单个对象格式相同

### 3. 创建猫粮

**请求**
```
POST /api/catfood/
Content-Type: application/json

{
  "name": "皇家猫粮",
  "brand": "Royal Canin",
  "desc": "适合成年猫的营养猫粮",
  "image_url": "http://example.com/image.jpg",
  "tags": ["成猫粮", "高蛋白"],
  "nutrition": [1, 2, 3],  // Ingredient IDs
  "additive": [1, 2],      // Additive IDs
  "safety": "安全性分析...",
  "nutrient": "营养分析...",
  "percentage": true,
  "percentData": {
    "crude_protein": 44.0,
    "crude_fat": 20.0,
    "crude_fiber": 1.8,
    "crude_ash": 8.7,
    "others": 10.0
  }
}
```

**响应**: 返回创建的猫粮完整信息（格式同详情）

### 4. 更新猫粮

**完整更新**
```
PUT /api/catfood/{id}/
Content-Type: application/json

{
  "name": "更新后的名称",
  "brand": "更新后的品牌",
  "desc": "更新后的描述",
  // ... 其他字段
}
```

**部分更新**
```
PATCH /api/catfood/{id}/
Content-Type: application/json

{
  "name": "只更新名称"
}
```

**响应**: 返回更新后的猫粮完整信息

### 5. 根据名称搜索猫粮

**请求**
```
GET /api/catfood/search/?name=皇家
```

**查询参数**
- `name` (必填): 搜索关键词，支持模糊搜索（搜索名称和品牌）

**响应**: 返回匹配的猫粮列表

### 6. 获取某个猫粮的所有评论

**请求**
```
GET /api/catfood/{id}/comments/
```

**响应示例**
```json
[
  {
    "id": 1,
    "content": "这个猫粮很不错！",
    "author": {
      "id": 1,
      "username": "user123",
      "avatar": "http://example.com/avatar.jpg"
    },
    "createdAt": "2024-01-01T00:00:00Z",
    "likes": 10,
    "isLiked": false,
    "target_type": "catfood",
    "target_id": 1
  }
]
```

### 7. 删除猫粮

**请求**
```
DELETE /api/catfood/{id}/
```

**响应**: 204 No Content

---

## 评论 API

### 1. 获取评论列表

**请求**
```
GET /api/comments/
```

**查询参数（可选）**
- `target_type`: 过滤目标类型（post/catfood/report）
- `target_id`: 过滤目标 ID

**示例**
```
GET /api/comments/?target_type=catfood&target_id=1
```

**响应**: 返回评论列表（格式同上）

### 2. 创建评论

**请求**
```
POST /api/comments/
Authorization: Bearer {token}
Content-Type: application/json

{
  "content": "这个猫粮很不错！",
  "targetId": 1,
  "targetType": "catfood"  // post/catfood/report
}
```

**响应**: 返回创建的评论完整信息

**注意**: 此接口需要用户登录认证

### 3. 更新评论

**请求**
```
PUT /api/comments/{id}/
Authorization: Bearer {token}
Content-Type: application/json

{
  "content": "更新后的评论内容"
}
```

**响应**: 返回更新后的评论信息

**权限**: 仅评论作者可以更新

### 4. 删除评论

**请求**
```
DELETE /api/comments/{id}/
Authorization: Bearer {token}
```

**响应**: 204 No Content

**权限**: 仅评论作者可以删除

### 5. 点赞/取消点赞评论

**请求**
```
POST /api/comments/{id}/like/
Authorization: Bearer {token}
```

**响应示例**
```json
{
  "action": "liked",  // 或 "unliked"
  "likes": 11,
  "comment": {
    "id": 1,
    "content": "这个猫粮很不错！",
    "author": {
      "id": 1,
      "username": "user123",
      "avatar": "http://example.com/avatar.jpg"
    },
    "createdAt": "2024-01-01T00:00:00Z",
    "likes": 11,
    "isLiked": true,
    "target_type": "catfood",
    "target_id": 1
  }
}
```

**说明**: 
- 如果未点赞，则添加点赞
- 如果已点赞，则取消点赞
- 返回操作类型和更新后的点赞数

**注意**: 此接口需要用户登录认证

---

## 错误响应

所有 API 在发生错误时会返回相应的 HTTP 状态码和错误信息：

```json
{
  "error": "错误描述信息"
}
```

常见状态码：
- `200 OK`: 请求成功
- `201 Created`: 创建成功
- `204 No Content`: 删除成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未认证
- `403 Forbidden`: 无权限
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器错误

---

## 认证说明

需要认证的接口需要在请求头中添加 JWT Token：

```
Authorization: Bearer {your_access_token}
```

获取 Token 的方式请参考用户认证 API 文档。

---

## 分页

列表接口支持分页，可以通过查询参数控制：

```
GET /api/catfood/?page=2&page_size=10
```

分页响应格式：
```json
{
  "count": 100,
  "next": "http://api/catfood/?page=3",
  "previous": "http://api/catfood/?page=1",
  "results": [...]
}
```

