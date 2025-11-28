"""
AI分析报告序列化器
"""

from rest_framework import serializers

from .models import AIAnalysisReport, FavoriteReport


class AIAnalysisReportSerializer(serializers.ModelSerializer):
    """AI分析报告序列化器"""

    catfood_id = serializers.IntegerField(source="catfood.id", read_only=True)
    catfood_name = serializers.CharField(source="catfood.name", read_only=True)

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
            "percent_data",
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
