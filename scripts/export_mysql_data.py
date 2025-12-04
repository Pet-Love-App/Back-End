#!/usr/bin/env python3
"""
MySQL 数据导出脚本
将现有 MySQL 数据导出为 JSON 格式，便于导入 Supabase
"""

import os
import json
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path

# 添加项目根目录到 Python 路径
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# 设置 Django 环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "back_end.settings")
import django

django.setup()

from django.contrib.auth.models import User
from user.models import UserProfile, Pet
from catfood.models import (
    CatFood,
    CatFoodTag,
    CatFoodTagRelation,
    CatFoodIngredient,
    CatFoodAdditive,
    CatFoodRating,
    CatFoodFavorite,
)
from additive.models import Ingredient, Additive
from forum.models import Post, PostMedia, Favorite, Notification
from comment.models import Comment, CommentLike
from ai_report.models import AIAnalysisReport, FavoriteReport
from reputation.models import ReputationSummary, Badge, UserBadge

OUTPUT_DIR = BASE_DIR / "data_export"


def json_serializer(obj):
    """JSON 序列化辅助函数"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


def export_model(model_class, filename):
    """导出 Django Model 数据"""
    print(f"Exporting {model_class.__name__}...")

    # 获取所有对象
    queryset = model_class.objects.all()

    # 转换为字典列表
    data = []
    for obj in queryset:
        obj_dict = {}
        for field in obj._meta.fields:
            value = getattr(obj, field.name)

            # 处理外键
            if field.is_relation and value is not None:
                if hasattr(value, "id"):
                    obj_dict[field.name] = value.id
                else:
                    obj_dict[field.name] = str(value)
            else:
                obj_dict[field.name] = value

        data.append(obj_dict)

    # 保存到文件
    output_file = OUTPUT_DIR / filename
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=json_serializer)

    print(f"  ✓ Exported {len(data)} rows to {filename}")
    return len(data)


def main():
    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("=" * 60)
    print("MySQL Data Export Script")
    print("=" * 60)
    print()

    # 定义要导出的模型（按依赖顺序）
    export_tasks = [
        # 用户相关
        (User, "users.json"),
        (UserProfile, "user_profiles.json"),
        (Pet, "pets.json"),
        # 添加剂和营养成分
        (Ingredient, "ingredients.json"),
        (Additive, "additives.json"),
        # 猫粮
        (CatFood, "catfoods.json"),
        (CatFoodTag, "catfood_tags.json"),
        (CatFoodTagRelation, "catfood_tag_relations.json"),
        (CatFoodIngredient, "catfood_ingredients.json"),
        (CatFoodAdditive, "catfood_additives.json"),
        (CatFoodRating, "catfood_ratings.json"),
        (CatFoodFavorite, "catfood_favorites.json"),
        # 论坛
        (Post, "posts.json"),
        (PostMedia, "post_media.json"),
        (Favorite, "post_favorites.json"),
        # 评论
        (Comment, "comments.json"),
        (CommentLike, "comment_likes.json"),
        # 通知
        (Notification, "notifications.json"),
        # AI 报告
        (AIAnalysisReport, "ai_analysis_reports.json"),
        (FavoriteReport, "favorite_reports.json"),
        # 信誉系统
        (ReputationSummary, "reputation_summaries.json"),
        (Badge, "badges.json"),
        (UserBadge, "user_badges.json"),
    ]

    total_rows = 0
    for model_class, filename in export_tasks:
        try:
            count = export_model(model_class, filename)
            total_rows += count
        except Exception as e:
            print(f"  ✗ Error exporting {model_class.__name__}: {e}")

    print()
    print("=" * 60)
    print(f"✓ Export completed! Total rows: {total_rows}")
    print(f"Data exported to: {OUTPUT_DIR}/")
    print("=" * 60)


if __name__ == "__main__":
    main()

