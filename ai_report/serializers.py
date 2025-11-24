"""
AI分析报告序列化器
"""

from rest_framework import serializers

from .models import AIAnalysisReport, FavoriteReport


class AIAnalysisReportSerializer(serializers.ModelSerializer):
    """AI分析报告序列化器"""

    catfood_id = serializers.IntegerField(source="catfood.id", read_only=True)
    catfood_name = serializers.CharField(source="catfood.name", read_only=True)

    percent_data = serializers.SerializerMethodField()

    class Meta:
        model = AIAnalysisReport
        fields = [
            "id",
            "catfood_id",
            "catfood_name",
            "ingredients_text",
            "tags",
            "additives",
            "ingredients",
            "safety",
            "nutrient",
            "percentage",
            "percent_data",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_percent_data(self, obj):
        """返回百分比数据"""
        return {
            "crude_protein": float(obj.crude_protein) if obj.crude_protein else None,
            "crude_fat": float(obj.crude_fat) if obj.crude_fat else None,
            "carbohydrates": float(obj.carbohydrates) if obj.carbohydrates else None,
            "crude_fiber": float(obj.crude_fiber) if obj.crude_fiber else None,
            "crude_ash": float(obj.crude_ash) if obj.crude_ash else None,
            "others": float(obj.others) if obj.others else None,
        }


class AIAnalysisReportCreateSerializer(serializers.ModelSerializer):
    """创建AI分析报告的序列化器"""

    class Meta:
        model = AIAnalysisReport
        fields = [
            "catfood",
            "ingredients_text",
            "tags",
            "additives",
            "ingredients",
            "safety",
            "nutrient",
            "percentage",
            "crude_protein",
            "crude_fat",
            "carbohydrates",
            "crude_fiber",
            "crude_ash",
            "others",
        ]


class FavoriteReportSerializer(serializers.ModelSerializer):
    """AI报告收藏序列化器"""

    report = AIAnalysisReportSerializer(read_only=True)

    class Meta:
        model = FavoriteReport
        fields = [
            "id",
            "report",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
