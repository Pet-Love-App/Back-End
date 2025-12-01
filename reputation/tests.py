# reputation/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.exceptions import ImproperlyConfigured

from rest_framework.test import APIClient

from .models import ReputationSummary, Badge, UserBadge
from .services import compute_user_reputation, evaluate_badge_rule, get_runtime_metrics

# 项目内依赖（尽量减少对具体类名的硬编码）
from comment.models import Comment, CommentLike

User = get_user_model()


def ensure_profile_for_user(user):
    """
    尝试通过 user.profile 访问用户资料；如不存在，尝试用常见的类名创建。
    请确保你项目中的用户资料模型与 User OneToOne 关联的 related_name 为 'profile'。
    若不是，请将 services.py 中的 getattr(user, "profile", None) 与此函数同步修改。
    """
    profile = getattr(user, "profile", None)
    if profile:
        return profile

    # 回退尝试常见类名：Profile 或 UserProfile
    created = False
    for cls_name in ("Profile", "UserProfile"):
        try:
            from user.models import (
                Profile as ProfileModel,  # noqa: F401
            )
            klass = getattr(__import__("user.models", fromlist=[cls_name]), cls_name)
        except Exception:
            # 再尝试 UserProfile
            try:
                klass = getattr(__import__("user.models", fromlist=["UserProfile"]), "UserProfile")
            except Exception:
                klass = None
        if klass:
            profile = klass.objects.create(user=user)
            created = True
            break

    if not profile:
        # 无法自动创建，给出明确提示，指导开发者调整
        raise ImproperlyConfigured(
            "未能通过 user.profile 或常见类名(Profile/UserProfile)创建资料。"
            "请确保用户资料模型存在，且与 User 的 OneToOneField 设置 related_name='profile'，"
            "或在本测试的 ensure_profile_for_user 中使用你的实际类名。"
        )
    return profile


class ReputationCalculationTests(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
        )

        # 确保存在可访问的资料对象，并填充资料字段
        profile = ensure_profile_for_user(self.user)
        # 给出可能存在的字段赋值（若某字段不存在，忽略异常）
        for field, value in [("avatar", "test.jpg"), ("bio", "Test bio"), ("phone", "123456789")]:
            try:
                setattr(profile, field, value)
            except Exception:
                pass
        try:
            profile.save()
        except Exception:
            pass

        # 如你的 Pet 模型在 user.models 中，请导入并创建宠物
        # 注意：services.py 从 user.models 导入 Pet，这里保持一致
        try:
            from user.models import Pet
            self.pet = Pet.objects.create(user=self.user, name="Test Pet")
        except Exception:
            # 若不存在 Pet 模型，测试仍可继续，但 profile_completeness 会少一项
            self.pet = None

        # 创建评论与点赞（15条评论，前10条各1个赞）
        self.comments = [
            Comment.objects.create(author=self.user, content=f"Comment {i}")
            for i in range(15)
        ]
        for comment in self.comments[:10]:
            CommentLike.objects.create(comment=comment)

    def test_profile_completeness_calculation(self):
        """测试个人资料完整性计算（头像、简介、手机、至少一只宠物）"""
        summary = compute_user_reputation(self.user)
        # 若项目中不存在 Pet 模型，则满分会少一项；这里做宽松断言（>= 15）
        self.assertTrue(15 <= summary.profile_completeness <= 20)

    def test_review_quality_calculation(self):
        """测试评论质量计算"""
        summary = compute_user_reputation(self.user)
        self.assertTrue(0 < summary.review_quality <= 40)

    def test_badge_evaluation_and_grant(self):
        """测试徽章评估规则与授予"""
        # 创建启用的徽章，规则：至少10条评论
        badge = Badge.objects.create(
            code="comment_master",
            name="评论大师",
            description="发表至少10条评论",
            enabled=True,
            rule={
                "type": "all_of",
                "conditions": [
                    {"kind": "comments_at_least", "value": 10}
                ],
            },
        )

        summary = compute_user_reputation(self.user)
        metrics = get_runtime_metrics(self.user)

        # 评估应通过
        self.assertTrue(evaluate_badge_rule(self.user, summary, badge, metrics))

        # ensure_badges 在 compute_user_reputation 内已触发，用户应已获得该徽章
        self.assertTrue(UserBadge.objects.filter(user=self.user, badge=badge).exists())

    def test_level_calculation(self):
        """测试等级计算逻辑"""
        summary = compute_user_reputation(self.user)
        # 根据当前积分模型，该用户至少应到 intermediate 或更高
        self.assertIn(summary.level, ["intermediate", "advanced", "expert"])


class ReputationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # 管理员登录
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass",
        )
        self.client.login(username="admin", password="adminpass")

        # 普通用户
        self.user = User.objects.create_user(
            username="apiuser",
            password="userpass",
        )

        # 为普通用户创建基础数据，避免空资料导致某些逻辑分支出问题
        profile = ensure_profile_for_user(self.user)
        try:
            setattr(profile, "avatar", "u.jpg")
            setattr(profile, "bio", "bio")
            setattr(profile, "phone", "18800000000")
            profile.save()
        except Exception:
            pass

        try:
            from user.models import Pet
            Pet.objects.create(user=self.user, name="U Pet")
        except Exception:
            pass

    def test_recompute_user_api(self):
        """测试重算用户信誉的管理接口"""
        # 直接访问路由 /reputation/admin/recompute_user/
        resp = self.client.post("/reputation/admin/recompute_user/", {"user_id": self.user.id}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("已重算用户", resp.data.get("message", ""))

    def test_badge_management_enable_disable(self):
        """测试徽章启用/禁用接口"""
        badge = Badge.objects.create(code="test_badge", name="Test Badge", enabled=False)

        # 启用
        resp = self.client.post(f"/reputation/badges/{badge.id}/enable/")
        self.assertEqual(resp.status_code, 200)
        badge.refresh_from_db()
        self.assertTrue(badge.enabled)

        # 禁用
        resp = self.client.post(f"/reputation/badges/{badge.id}/disable/")
        self.assertEqual(resp.status_code, 200)
        badge.refresh_from_db()
        self.assertFalse(badge.enabled)

    def test_equip_and_unequip_badge_flow(self):
        """测试佩戴/取消佩戴流程：未获得不能佩戴，获得后可佩戴与卸下"""
        # 先创建一个需要 reputation_score_at_least >= 1 的徽章，确保容易获得
        badge = Badge.objects.create(
            code="easy_badge",
            name="易得徽章",
            enabled=True,
            rule={
                "type": "all_of",
                "conditions": [
                    {"kind": "reputation_score_at_least", "value": 1}
                ],
            },
        )

        # 切换为普通用户上下文进行接口调用
        self.client.logout()
        self.client.login(username="apiuser", password="userpass")

        # 未获得时尝试佩戴，应 403
        resp = self.client.post(f"/reputation/badges/{badge.code}/equip/")
        self.assertEqual(resp.status_code, 403)

        # 重算信誉，触发授予（ensure_badges）
        compute_user_reputation(self.user)
        self.assertTrue(UserBadge.objects.filter(user=self.user, badge=badge).exists())

        # 再次佩戴，应成功
        resp = self.client.post(f"/reputation/badges/{badge.code}/equip/")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(UserBadge.objects.get(user=self.user, badge=badge).is_equipped)

        # 取消佩戴，应成功
        resp = self.client.post(f"/reputation/badges/{badge.code}/unequip/")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(UserBadge.objects.get(user=self.user, badge=badge).is_equipped)


class ReputationAPIEdgeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="u1", password="p1")
        self.admin = User.objects.create_superuser(username="adm", email="a@a.com", password="ap")

    def test_me_requires_auth(self):
        resp = self.client.get("/reputation/me/")
        # 未认证，可能返回 401 或 403（取决于全局认证设置）
        self.assertIn(resp.status_code, (401, 403))

    def test_my_badges_requires_auth(self):
        resp = self.client.get("/reputation/my-badges/")
        self.assertIn(resp.status_code, (401, 403))

    def test_user_reputation_allow_any(self):
        # 匿名也可访问别人的概览（当前策略），存在则 200
        # 先确保该用户有概览
        compute_user_reputation(self.user)
        resp = self.client.get(f"/reputation/users/{self.user.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("score", resp.data)

    def test_admin_only_recompute(self):
        self.client.login(username="u1", password="p1")
        resp = self.client.post("/reputation/admin/recompute_user/", {"user_id": self.user.id}, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_badge_rule_unknown_kind(self):
        b = Badge.objects.create(code="r2", name="R2", enabled=True,
            rule={"type":"all_of","conditions":[{"kind":"unknown_kind","value":123}]})

        s = compute_user_reputation(self.user)
        m = get_runtime_metrics(self.user)
        self.assertFalse(evaluate_badge_rule(self.user, s, b, m))

    def test_badge_rule_one_of_logic(self):
        # one_of：任一条件满足即可
        b = Badge.objects.create(code="r3", name="R3", enabled=True,
            rule={"type":"one_of","conditions":[
                {"kind":"comments_at_least","value":1},
                {"kind":"reputation_score_at_least","value":0}
            ]})
        s = compute_user_reputation(self.user)
        m = get_runtime_metrics(self.user)
        self.assertTrue(evaluate_badge_rule(self.user, s, b, m))

    def test_badge_rule_empty_conditions(self):
        b = Badge.objects.create(code="r4", name="R4", enabled=True,
            rule={"type":"all_of","conditions":[]})
        s = compute_user_reputation(self.user)
        m = get_runtime_metrics(self.user)
        self.assertFalse(evaluate_badge_rule(self.user, s, b, m))