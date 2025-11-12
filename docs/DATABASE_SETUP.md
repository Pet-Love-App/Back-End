# 数据库设置指南

## 前提条件

确保你已经：
1. 安装了 Python 和相关依赖
2. 配置好了数据库连接（MySQL 或 SQLite）
3. 激活了虚拟环境（如果使用）

## 运行迁移

### 1. 创建迁移文件

为新添加的 catfood 和 comment 应用创建迁移文件：

```bash
# 创建 catfood 迁移
python manage.py makemigrations catfood

# 创建 comment 迁移
python manage.py makemigrations comment
```

### 2. 应用迁移

将迁移应用到数据库：

```bash
python manage.py migrate
```

这将创建以下数据表：

#### CatFood 相关表：
- `catfood` - 猫粮主表
- `catfood_tag` - 猫粮标签表
- `catfood_tag_relation` - 猫粮和标签的关系表
- `catfood_ingredient` - 猫粮和营养成分的关系表
- `catfood_additive` - 猫粮和添加剂的关系表
- `catfood_rating` - 猫粮评分表

#### Comment 相关表：
- `comment` - 评论表
- `comment_like` - 评论点赞表

### 3. 创建超级用户（可选）

如果需要访问 Django Admin：

```bash
python manage.py createsuperuser
```

### 4. 启动开发服务器

```bash
python manage.py runserver
```

服务器将在 `http://127.0.0.1:8000` 启动。

## 验证安装

访问以下 URL 验证 API 是否正常工作：

1. **猫粮列表**: `http://127.0.0.1:8000/api/catfood/`
2. **评论列表**: `http://127.0.0.1:8000/api/comments/`
3. **Django Admin**: `http://127.0.0.1:8000/admin/`

## 数据库结构

### CatFood 模型字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| name | CharField | 猫粮名称 |
| brand | CharField | 品牌名称 |
| desc | TextField | 简介描述 |
| image_url | URLField | 图片URL |
| score | DecimalField | 评分（0-5分）|
| count_num | IntegerField | 评分人数 |
| percentage | BooleanField | 是否能生成图表 |
| crude_protein | DecimalField | 粗蛋白含量 |
| crude_fat | DecimalField | 粗脂肪含量 |
| carbohydrates | DecimalField | 碳水化合物含量 |
| crude_fiber | DecimalField | 粗纤维含量 |
| crude_ash | DecimalField | 粗灰分含量 |
| others | DecimalField | 其他成分含量 |
| safety | TextField | 安全性分析 |
| nutrient | TextField | 营养分析 |
| created_at | DateTimeField | 创建时间 |
| updated_at | DateTimeField | 更新时间 |

### Comment 模型字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| content | TextField | 评论内容 |
| author | ForeignKey | 作者（User）|
| target_type | CharField | 目标类型（post/catfood/report）|
| target_id | IntegerField | 目标ID |
| likes | IntegerField | 点赞数 |
| created_at | DateTimeField | 创建时间 |
| updated_at | DateTimeField | 更新时间 |

## 常见问题

### Q: 迁移失败，提示表已存在

A: 如果表已经存在，可以使用 `--fake` 标记迁移：

```bash
python manage.py migrate --fake
```

### Q: 如何重置数据库？

A: 删除所有迁移文件和数据库，然后重新创建：

```bash
# 删除迁移文件（保留 __init__.py）
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# 删除数据库（SQLite）
rm db.sqlite3

# 重新创建迁移
python manage.py makemigrations
python manage.py migrate
```

### Q: 如何查看当前迁移状态？

A: 使用以下命令：

```bash
python manage.py showmigrations
```

## 数据填充（可选）

如果需要测试数据，可以创建一个数据填充脚本：

```bash
python manage.py shell
```

然后在 Python shell 中执行：

```python
from catfood.models import CatFood
from comment.models import Comment
from django.contrib.auth.models import User

# 创建测试猫粮
catfood = CatFood.objects.create(
    name="测试猫粮",
    brand="测试品牌",
    desc="这是一个测试猫粮",
    percentage=True,
    crude_protein=44.0,
    crude_fat=20.0
)

# 创建测试用户和评论
user = User.objects.create_user('testuser', 'test@example.com', 'password')
comment = Comment.objects.create(
    content="很不错的猫粮！",
    author=user,
    target_type="catfood",
    target_id=catfood.id
)

print("测试数据创建成功！")
```

## 下一步

参考 `API_CATFOOD_COMMENT.md` 文档了解如何使用这些 API。

