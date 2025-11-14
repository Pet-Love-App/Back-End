"""
Django management command to import cat food data from JSON file
导入猫粮数据的管理命令
"""

import json

from django.core.management.base import BaseCommand
from django.db import transaction

from catfood.models import CatFood


class Command(BaseCommand):
    help = "从JSON文件导入猫粮数据（仅导入基本信息：名称、品牌、图片）"

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file",
            type=str,
            help="JSON文件路径（例如：docs/猫粮品牌完整汇总_已去重.json）",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="导入前清空现有数据",
        )

    def handle(self, *args, **options):
        json_file = options["json_file"]
        clear = options.get("clear", False)

        self.stdout.write(self.style.NOTICE(f"开始从 {json_file} 导入猫粮数据..."))

        try:
            # 读取JSON文件
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)

            products = data.get("商品列表", [])
            total_count = len(products)
            self.stdout.write(self.style.NOTICE(f"共发现 {total_count} 个商品"))

            if clear:
                confirm = input("确定要清空现有数据吗？(yes/no): ")
                if confirm.lower() == "yes":
                    deleted_count = CatFood.objects.all().delete()[0]
                    self.stdout.write(self.style.WARNING(f"已删除 {deleted_count} 条现有记录"))
                else:
                    self.stdout.write(self.style.ERROR("已取消清空操作"))
                    return

            # 批量导入
            success_count = 0
            skip_count = 0
            error_count = 0

            with transaction.atomic():
                for index, product in enumerate(products, 1):
                    try:
                        brand = product.get("品牌", "")
                        name = product.get("商品名称", "")
                        image_url = product.get("封面图片链接", "")

                        if not name:
                            self.stdout.write(
                                self.style.WARNING(f"[{index}/{total_count}] 跳过：缺少商品名称")
                            )
                            skip_count += 1
                            continue

                        # 检查是否已存在（品牌+名称组合唯一）
                        if CatFood.objects.filter(brand=brand, name=name).exists():
                            skip_count += 1
                            if index % 100 == 0:  # 每100个显示一次进度
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"[{index}/{total_count}] 跳过：{brand} - {name[:30]}... (已存在)"
                                    )
                                )
                            continue

                        # 创建猫粮记录（仅填充基本信息）
                        catfood = CatFood.objects.create(
                            name=name,
                            brand=brand,
                            image_url=image_url if image_url else None,
                            # 评分信息保持默认值
                            score=0,
                            count_num=0,
                            # 营养成分等待OCR扫描后填充
                            percentage=False,
                            crude_protein=None,
                            crude_fat=None,
                            carbohydrates=None,
                            crude_fiber=None,
                            crude_ash=None,
                            others=None,
                            # 分析内容留空
                            safety="",
                            nutrient="",
                        )

                        success_count += 1

                        # 每100个显示一次进度
                        if index % 100 == 0:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"[{index}/{total_count}] 成功导入：{brand} - {name[:30]}..."
                                )
                            )

                    except Exception as e:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f"[{index}/{total_count}] 导入失败：{product.get('商品名称', 'Unknown')} - {str(e)}"
                            )
                        )

            # 输出统计信息
            self.stdout.write("\n" + "=" * 80)
            self.stdout.write(self.style.SUCCESS("导入完成！"))
            self.stdout.write("=" * 80)
            self.stdout.write(f"总计: {total_count} 个商品")
            self.stdout.write(self.style.SUCCESS(f"✓ 成功导入: {success_count} 个"))
            self.stdout.write(self.style.WARNING(f"⊘ 跳过: {skip_count} 个（重复或无效）"))
            self.stdout.write(self.style.ERROR(f"✗ 失败: {error_count} 个"))
            self.stdout.write("=" * 80)

            self.stdout.write(
                self.style.NOTICE("\n提示：营养成分、添加剂等数据需要通过OCR扫描后调用API填充。")
            )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"错误：找不到文件 {json_file}"))
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"错误：JSON解析失败 - {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"错误：{str(e)}"))
