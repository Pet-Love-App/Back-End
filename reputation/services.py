import math
from typing import Any, Dict, List, Optional
from django.db import transaction
from django.contrib.auth import get_user_model

from .models import ReputationSummary, Badge, UserBadge

User = get_user_model()

MAX_PROFILE = 20
MAX_REVIEW = 40
MAX_CONTRIB = 30
MAX_COMPLIANCE = 10


def _safe_import_pet_model():
    try:
        from user.models import Pet  # type: ignore
        return Pet
    except Exception:
        return None


def _safe_import_comment_models():
    try:
        from comment.models import Comment, CommentLike  # type: ignore
        return Comment, CommentLike
    except Exception:
        return None, None


def calc_profile_completeness(user: User) -> int:
    filled = 0
    total = 4
    profile = getattr(user, "profile", None)
    if profile and getattr(profile, "avatar", None):
        filled += 1
    if profile and getattr(profile, "bio", ""):
        filled += 1
    if profile and getattr(profile, "phone", ""):
        filled += 1

    Pet = _safe_import_pet_model()
    if Pet is not None:
        try:
            if Pet.objects.filter(user=user).exists():
                filled += 1
        except Exception:
            # 容错：出现异常当作无宠物
            pass
    # 若无 Pet 模型，宠物维度计 0
    ratio = filled / total
    return round(ratio * MAX_PROFILE)


def calc_review_quality(user: User) -> int:
    Comment, CommentLike = _safe_import_comment_models()
    total_comments = 0
    helpful_votes = 0
    if Comment is not None and CommentLike is not None:
        try:
            total_comments = Comment.objects.filter(author=user).count()
            helpful_votes = CommentLike.objects.filter(comment__author=user).count()
        except Exception:
            total_comments = 0
            helpful_votes = 0
    helpful_ratio = helpful_votes / total_comments if total_comments else 0.0
    part1 = 10 * math.log10(1 + helpful_votes)
    part2 = 30 * min(1.0, helpful_ratio)
    return min(MAX_REVIEW, round(part1 + part2))


def calc_contribution(user: User) -> int:
    Comment, CommentLike = _safe_import_comment_models()
    comments = 0
    helpful_votes = 0
    if Comment is not None and CommentLike is not None:
        try:
            comments = Comment.objects.filter(author=user).count()
            helpful_votes = CommentLike.objects.filter(comment__author=user).count()
        except Exception:
            comments = 0
            helpful_votes = 0
    score = min(10, comments // 10) + min(20, helpful_votes // 20)
    return min(MAX_CONTRIB, score)


def calc_compliance(user: User) -> int:
    return MAX_COMPLIANCE


def level_from_score(score: int) -> str:
    if score >= 80:
        return "expert"
    if score >= 60:
        return "advanced"
    if score >= 40:
        return "intermediate"
    return "novice"


def get_runtime_metrics(user: User) -> dict:
    Comment, CommentLike = _safe_import_comment_models()
    Pet = _safe_import_pet_model()

    total_comments = 0
    helpful_votes = 0
    if Comment is not None and CommentLike is not None:
        try:
            total_comments = Comment.objects.filter(author=user).count()
            helpful_votes = CommentLike.objects.filter(comment__author=user).count()
        except Exception:
            total_comments = 0
            helpful_votes = 0

    profile = getattr(user, "profile", None)
    has_avatar = bool(getattr(profile, "avatar", None)) if profile else False
    has_bio = bool(getattr(profile, "bio", "")) if profile else False
    has_phone = bool(getattr(profile, "phone", "")) if profile else False

    pet_count = 0
    if Pet is not None:
        try:
            pet_count = Pet.objects.filter(user=user).count()
        except Exception:
            pet_count = 0

    return {
        "total_comments": total_comments,
        "helpful_votes": helpful_votes,
        "has_avatar": has_avatar,
        "has_bio": has_bio,
        "has_phone": has_phone,
        "pet_count": pet_count,
    }


def evaluate_badge_rule(user: User, summary: ReputationSummary, badge: 'Badge', metrics: dict) -> bool:
    """
    通用规则解释器：
    支持 type: one_of / all_of
    condition kinds:
      - reputation_level_at_least: value in ["novice","intermediate","advanced","expert"]
      - comment_likes_at_least: value: int
      - comments_at_least: value: int
      - profile_has_avatar: value: bool
      - profile_has_bio: value: bool
      - profile_has_phone: value: bool
      - has_pet_count_at_least: value: int
      - reputation_score_at_least: value: int
    """
    rule = badge.rule or {}
    conds = rule.get("conditions", []) or []
    mode = rule.get("type", "all_of")

    def check(c: dict) -> bool:
        kind = c.get("kind")
        value = c.get("value")
        if kind == "reputation_level_at_least":
            order = ["novice", "intermediate", "advanced", "expert"]
            try:
                return order.index(summary.level) >= order.index(value)
            except ValueError:
                return False
        if kind == "reputation_score_at_least":
            try:
                return summary.score >= int(value)
            except Exception:
                return False
        if kind == "comment_likes_at_least":
            try:
                return metrics.get("helpful_votes", 0) >= int(value)
            except Exception:
                return False
        if kind == "comments_at_least":
            try:
                return metrics.get("total_comments", 0) >= int(value)
            except Exception:
                return False
        if kind == "profile_has_avatar":
            return bool(metrics.get("has_avatar", False)) == bool(value)
        if kind == "profile_has_bio":
            return bool(metrics.get("has_bio", False)) == bool(value)
        if kind == "profile_has_phone":
            return bool(metrics.get("has_phone", False)) == bool(value)
        if kind == "has_pet_count_at_least":
            try:
                return metrics.get("pet_count", 0) >= int(value)
            except Exception:
                return False
        # 未知 kind：返回 False（同时可考虑记录日志）
        return False

    results = [check(c) for c in conds]
    if mode == "one_of":
        return any(results) if results else False
    # 默认 all_of
    return all(results) if results else False


@transaction.atomic
def compute_user_reputation(user: User) -> ReputationSummary:
    p = calc_profile_completeness(user)
    r = calc_review_quality(user)
    c = calc_contribution(user)
    k = calc_compliance(user)
    total = max(0, min(100, p + r + c + k))

    summary, _ = ReputationSummary.objects.select_for_update().get_or_create(user=user)
    summary.profile_completeness = p
    summary.review_quality = r
    summary.community_contribution = c
    summary.compliance = k
    summary.score = total
    summary.level = level_from_score(total)
    summary.save()

    ensure_badges(user, summary)
    return summary


def ensure_badges(user: User, summary: ReputationSummary):
    metrics = get_runtime_metrics(user)
    badges = Badge.objects.filter(enabled=True)

    for badge in badges:
        ok = evaluate_badge_rule(user, summary, badge, metrics)
        # 并发友好：get_or_create 防止 unique_together 冲突
        has = UserBadge.objects.filter(user=user, badge=badge).first()
        if ok and not has:
            UserBadge.objects.get_or_create(user=user, badge=badge, defaults={"is_equipped": False})
        elif not ok and has:
            # 策略：不回收已获得的徽章
            pass