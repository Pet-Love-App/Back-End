"""
API URL 配置
所有数据库操作通过 Supabase 实现
"""

from django.urls import path

from . import (
    additive_views,
    ai_report_views,
    auth_views,
    catfood_views,
    comment_views,
    forum_views,
    notification_views,
    ocr_views,
    pet_views,
    reputation_views,
)

urlpatterns = [
    # ==================== 认证相关 ====================
    path("auth/register/", auth_views.register, name="auth_register"),
    path("auth/login/", auth_views.login, name="auth_login"),
    path("auth/logout/", auth_views.logout, name="auth_logout"),
    path("auth/profile/", auth_views.get_profile, name="auth_profile"),
    path("auth/profile/update/", auth_views.update_profile, name="auth_profile_update"),
    path("auth/avatar/", auth_views.upload_avatar, name="auth_avatar"),
    path("auth/avatar/delete/", auth_views.delete_avatar, name="auth_avatar_delete"),
    path(
        "auth/password/change/", auth_views.change_password, name="auth_password_change"
    ),
    path(
        "auth/password/reset/",
        auth_views.reset_password_request,
        name="auth_password_reset",
    ),
    path("auth/refresh/", auth_views.refresh_token, name="auth_refresh"),
    # ==================== 宠物相关 ====================
    path("pets/", pet_views.list_pets, name="list_pets"),
    path("pets/create/", pet_views.create_pet, name="create_pet"),
    path("pets/<int:pet_id>/", pet_views.update_pet, name="update_pet"),
    path("pets/<int:pet_id>/delete/", pet_views.delete_pet, name="delete_pet"),
    path(
        "pets/<int:pet_id>/photo/", pet_views.upload_pet_photo, name="upload_pet_photo"
    ),
    path(
        "pets/<int:pet_id>/photo/delete/",
        pet_views.delete_pet_photo,
        name="delete_pet_photo",
    ),
    # ==================== 猫粮相关 ====================
    # CRUD
    path("catfoods/", catfood_views.list_catfoods, name="list_catfoods"),
    path("catfoods/create/", catfood_views.create_catfood, name="create_catfood"),
    path(
        "catfoods/<int:catfood_id>/",
        catfood_views.get_catfood_detail,
        name="get_catfood_detail",
    ),
    path(
        "catfoods/<int:catfood_id>/update/",
        catfood_views.update_catfood,
        name="update_catfood",
    ),
    path(
        "catfoods/<int:catfood_id>/delete/",
        catfood_views.delete_catfood,
        name="delete_catfood",
    ),
    # 评分和收藏
    path(
        "catfoods/<int:catfood_id>/rate/",
        catfood_views.rate_catfood,
        name="rate_catfood",
    ),
    path(
        "catfoods/<int:catfood_id>/my-rating/",
        catfood_views.get_my_rating,
        name="get_my_rating",
    ),
    path(
        "catfoods/<int:catfood_id>/favorite/",
        catfood_views.favorite_catfood,
        name="favorite_catfood",
    ),
    path(
        "catfoods/favorites/",
        catfood_views.get_user_favorites,
        name="get_user_favorites",
    ),
    path(
        "catfoods/<int:catfood_id>/ratings/",
        catfood_views.get_catfood_ratings,
        name="get_catfood_ratings",
    ),
    # 猫粮点赞
    path("catfood/likes/", catfood_views.catfood_likes, name="catfood_likes"),
    path(
        "catfood/likes/<int:like_id>/",
        catfood_views.unlike_catfood,
        name="unlike_catfood",
    ),
    path(
        "catfood/likes/toggle/",
        catfood_views.toggle_like_catfood,
        name="toggle_like_catfood",
    ),
    path(
        "catfood/likes/check/",
        catfood_views.check_like_status,
        name="check_like_status",
    ),
    path(
        "catfood/likes/count/<int:catfood_id>/",
        catfood_views.get_catfood_likes_count,
        name="get_catfood_likes_count",
    ),
    # 条形码功能
    path(
        "catfood/by-barcode/",
        catfood_views.get_catfood_by_barcode,
        name="get_catfood_by_barcode",
    ),
    path("catfood/scan-barcode/", catfood_views.scan_barcode, name="scan_barcode"),
    # 猫粮评论快捷接口
    path(
        "catfood/<int:catfood_id>/comments/",
        catfood_views.get_catfood_comments,
        name="get_catfood_comments",
    ),
    # ==================== 论坛相关 ====================
    path("posts/", forum_views.list_posts, name="list_posts"),
    path("posts/create/", forum_views.create_post, name="create_post"),
    path(
        "posts/favorites/",
        forum_views.get_my_favorite_posts,
        name="get_my_favorite_posts",
    ),
    path("posts/<int:post_id>/", forum_views.get_post_detail, name="get_post_detail"),
    path("posts/<int:post_id>/delete/", forum_views.delete_post, name="delete_post"),
    path(
        "posts/<int:post_id>/favorite/", forum_views.favorite_post, name="favorite_post"
    ),
    # 论坛标签
    path("tags/", forum_views.list_tags, name="list_tags"),
    path("tags/<int:tag_id>/", forum_views.get_tag_detail, name="get_tag_detail"),
    # ==================== 评论相关 ====================
    path("comments/", comment_views.list_comments, name="list_comments"),
    path("comments/create/", comment_views.create_comment, name="create_comment"),
    path(
        "comments/<int:comment_id>/delete/",
        comment_views.delete_comment,
        name="delete_comment",
    ),
    path(
        "comments/<int:comment_id>/like/",
        comment_views.like_comment,
        name="like_comment",
    ),
    # ==================== AI 报告相关 ====================
    path("ai/llm/chat/", ai_report_views.llm_chat, name="ai_llm_chat"),
    path("ai/save/", ai_report_views.save_report, name="ai_save_report"),
    path("ai/<int:catfood_id>/", ai_report_views.get_report, name="ai_get_report"),
    path(
        "ai/<int:catfood_id>/exists/",
        ai_report_views.check_report_exists,
        name="ai_check_report_exists",
    ),
    path(
        "ai/<int:catfood_id>/delete/",
        ai_report_views.delete_report,
        name="ai_delete_report",
    ),
    path(
        "ai/favorites/",
        ai_report_views.get_favorite_reports,
        name="ai_get_favorite_reports",
    ),
    path(
        "ai/favorites/toggle/",
        ai_report_views.toggle_favorite_report,
        name="ai_toggle_favorite_report",
    ),
    path(
        "ai/favorites/<int:favorite_id>/",
        ai_report_views.delete_favorite_report,
        name="ai_delete_favorite_report",
    ),
    path(
        "ai/favorites/check/<int:report_id>/",
        ai_report_views.check_favorite_report,
        name="ai_check_favorite_report",
    ),
    # ==================== 添加剂/成分相关 ====================
    path(
        "additive/search-additive/",
        additive_views.search_additive,
        name="search_additive",
    ),
    path(
        "additive/search-ingredient/",
        additive_views.search_ingredient,
        name="search_ingredient",
    ),
    path(
        "additive/add-ingredient/", additive_views.add_ingredient, name="add_ingredient"
    ),
    path("additive/add-additive/", additive_views.add_additive, name="add_additive"),
    path(
        "search/ingredient/info",
        additive_views.get_ingredient_info,
        name="get_ingredient_info",
    ),
    # ==================== OCR 识别相关 ====================
    path("ocr/recognize/", ocr_views.ocr_recognize, name="ocr_recognize"),
    # ==================== 信誉系统相关 ====================
    path(
        "reputation/me/", reputation_views.get_my_reputation, name="get_my_reputation"
    ),
    path(
        "reputation/users/<str:user_id>/",
        reputation_views.get_user_reputation,
        name="get_user_reputation",
    ),
    path("reputation/my-badges/", reputation_views.get_my_badges, name="get_my_badges"),
    path(
        "reputation/badges/", reputation_views.list_all_badges, name="list_all_badges"
    ),
    path(
        "reputation/badges/<str:badge_code>/equip/",
        reputation_views.equip_badge,
        name="equip_badge",
    ),
    path(
        "reputation/badges/<str:badge_code>/unequip/",
        reputation_views.unequip_badge,
        name="unequip_badge",
    ),
    path(
        "reputation/admin/update/",
        reputation_views.update_reputation,
        name="update_reputation",
    ),
    path(
        "reputation/admin/award-badge/",
        reputation_views.award_badge,
        name="award_badge",
    ),
    # ==================== 通知系统相关 ====================
    path(
        "notifications/",
        notification_views.list_notifications,
        name="list_notifications",
    ),
    path(
        "notifications/unread-count/",
        notification_views.get_unread_count,
        name="get_unread_count",
    ),
    # 兼容旧路径（下划线版本）
    path(
        "notifications/unread_count/",
        notification_views.get_unread_count,
        name="get_unread_count_compat",
    ),
    path(
        "notifications/<int:notification_id>/",
        notification_views.get_notification_detail,
        name="get_notification_detail",
    ),
    path(
        "notifications/<int:notification_id>/read/",
        notification_views.mark_as_read,
        name="mark_notification_as_read",
    ),
    # 兼容旧路径（mark_read）
    path(
        "notifications/<int:notification_id>/mark_read/",
        notification_views.mark_as_read,
        name="mark_notification_as_read_compat",
    ),
    path(
        "notifications/read-all/",
        notification_views.mark_all_as_read,
        name="mark_all_as_read",
    ),
    # 兼容旧路径（mark_all_read）
    path(
        "notifications/mark_all_read/",
        notification_views.mark_all_as_read,
        name="mark_all_as_read_compat",
    ),
    path(
        "notifications/<int:notification_id>/delete/",
        notification_views.delete_notification,
        name="delete_notification",
    ),
    path(
        "notifications/delete-all/",
        notification_views.delete_all_notifications,
        name="delete_all_notifications",
    ),
    path(
        "notifications/create/",
        notification_views.create_notification,
        name="create_notification",
    ),
]
