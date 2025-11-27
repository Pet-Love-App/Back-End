"""
创建管理员用户的 Django 管理命令

使用方法:
    python manage.py create_admin --username admin --password your_password

企业最佳实践:
- 使用 Django 的 management command 框架
- 密码必须满足安全要求（至少6个字符）
- 自动创建 UserProfile 并设置 is_admin=True
- 提供清晰的成功/失败提示
"""

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from user.models import UserProfile


class Command(BaseCommand):
    help = "创建管理员用户（可以更新已有营养成分信息的猫粮）"

    def add_arguments(self, parser):
        """添加命令行参数"""
        parser.add_argument(
            "--username",
            type=str,
            required=True,
            help="管理员用户名（至少3个字符）",
        )
        parser.add_argument(
            "--password",
            type=str,
            required=True,
            help="管理员密码（至少6个字符）",
        )
        parser.add_argument(
            "--email",
            type=str,
            default="",
            help="管理员邮箱（可选）",
        )

    def handle(self, *args, **options):
        """执行命令"""
        username = options["username"]
        password = options["password"]
        email = options.get("email", "")

        # 验证用户名长度
        if len(username) < 3:
            raise CommandError("用户名至少需要3个字符")

        # 验证密码长度
        if len(password) < 6:
            raise CommandError("密码至少需要6个字符")

        # 检查用户是否已存在
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'用户 "{username}" 已存在，正在更新为管理员权限...')
            )
            user = User.objects.get(username=username)
            # 更新密码
            user.set_password(password)
            if email:
                user.email = email
            user.save()

            # 确保有 profile 并设置 is_admin
            profile, created = UserProfile.objects.get_or_create(user=user)
            if not profile.is_admin:
                profile.is_admin = True
                profile.save()
                self.stdout.write(self.style.SUCCESS(f'✅ 用户 "{username}" 已升级为管理员'))
            else:
                self.stdout.write(self.style.SUCCESS(f'✅ 用户 "{username}" 已经是管理员'))
        else:
            # 创建新用户
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
            )

            # 创建 profile 并设置为管理员
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.is_admin = True
            profile.save()

            self.stdout.write(self.style.SUCCESS(f'✅ 管理员用户 "{username}" 创建成功！'))

        # 显示登录信息
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("管理员账户信息:"))
        self.stdout.write(f"  用户名: {username}")
        self.stdout.write(f"  密码: {password}")
        self.stdout.write("  管理员权限: ✅ 已启用")
        self.stdout.write("\n权限说明:")
        self.stdout.write("  • 可以更新已有营养成分信息的猫粮")
        self.stdout.write("  • 可以覆盖其他用户保存的AI报告")
        self.stdout.write("=" * 60 + "\n")
