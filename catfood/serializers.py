"""
猫粮相关序列化器
"""

from rest_framework import serializers

from additive.models import Additive, Ingredient

from .models import (
    CatFood,
    CatFoodAdditive,
    CatFoodIngredient,
    CatFoodTag,
    CatFoodTagRelation,
)


class IngredientSerializer(serializers.ModelSerializer):
    """营养成分序列化器"""

    class Meta:
        model = Ingredient
        fields = ["id", "name", "type", "label", "desc"]


class AdditiveSerializer(serializers.ModelSerializer):
    """添加剂序列化器"""

    class Meta:
        model = Additive
        fields = ["id", "name", "en_name", "applicable_range", "type"]


class CatFoodTagSerializer(serializers.ModelSerializer):
    """猫粮标签序列化器"""

    class Meta:
        model = CatFoodTag
        fields = ["id", "name", "description"]


class PercentDataSerializer(serializers.Serializer):
    """百分比数据序列化器"""

    crude_protein = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True
    )
    crude_fat = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True
    )
    carbohydrates = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True
    )
    crude_fiber = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True
    )
    crude_ash = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True
    )
    others = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True
    )


class CatFoodSerializer(serializers.ModelSerializer):
    """
    猫粮序列化器（用于列表和详情显示）
    """

    tags = serializers.SerializerMethodField()
    nutrition = serializers.SerializerMethodField()
    additive = serializers.SerializerMethodField()
    percentData = serializers.SerializerMethodField()
    countNum = serializers.IntegerField(source="count_num", read_only=True)
    imageUrl = serializers.URLField(
        source="image_url", required=False, allow_null=True, allow_blank=True
    )

    class Meta:
        model = CatFood
        fields = [
            "id",
            "name",
            "brand",
            "desc",
            "score",
            "countNum",
            "imageUrl",
            "tags",
            "nutrition",
            "additive",
            "safety",
            "nutrient",
            "percentage",
            "percentData",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "score", "countNum"]

    def get_tags(self, obj):
        """获取标签列表"""
        tag_relations = obj.tag_relations.all()
        return CatFoodTagSerializer([rel.tag for rel in tag_relations], many=True).data

    def get_nutrition(self, obj):
        """获取营养成分列表"""
        ingredients = obj.ingredients.all().order_by("order")
        return IngredientSerializer([ing.ingredient for ing in ingredients], many=True).data

    def get_additive(self, obj):
        """获取添加剂列表"""
        additives = obj.additives.all().order_by("order")
        return AdditiveSerializer([add.additive for add in additives], many=True).data

    def get_percentData(self, obj):
        """获取百分比数据"""
        return {
            "crude_protein": obj.crude_protein,
            "crude_fat": obj.crude_fat,
            "carbohydrates": obj.carbohydrates,
            "crude_fiber": obj.crude_fiber,
            "crude_ash": obj.crude_ash,
            "others": obj.others,
        }


class CatFoodCreateUpdateSerializer(serializers.ModelSerializer):
    """
    猫粮创建和更新序列化器
    """

    tags = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    nutrition = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )
    additive = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )
    percentData = PercentDataSerializer(required=False)
    imageUrl = serializers.URLField(
        source="image_url", required=False, allow_null=True, allow_blank=True
    )

    class Meta:
        model = CatFood
        fields = [
            "id",
            "name",
            "brand",
            "desc",
            "imageUrl",
            "tags",
            "nutrition",
            "additive",
            "safety",
            "nutrient",
            "percentage",
            "percentData",
        ]
        read_only_fields = ["id"]

    def validate(self, data):
        """验证数据"""
        # 检查品牌+名称是否已存在（创建时）
        if not self.instance:  # 仅在创建时检查
            name = data.get("name")
            brand = data.get("brand", "")
            if CatFood.objects.filter(name=name, brand=brand).exists():
                raise serializers.ValidationError(
                    {"name": f'品牌"{brand}"的猫粮"{name}"已存在，不能重复添加'}
                )
        return data

    def create(self, validated_data):
        """创建猫粮"""
        tags = validated_data.pop("tags", [])
        nutrition = validated_data.pop("nutrition", [])
        additive = validated_data.pop("additive", [])
        percent_data = validated_data.pop("percentData", {})

        # 处理百分比数据
        if percent_data:
            validated_data.update(percent_data)

        # 创建猫粮实例
        catfood = CatFood.objects.create(**validated_data)

        # 处理标签
        self._handle_tags(catfood, tags)

        # 处理营养成分
        self._handle_nutrition(catfood, nutrition)

        # 处理添加剂
        self._handle_additives(catfood, additive)

        return catfood

    def update(self, instance, validated_data):
        """更新猫粮"""
        tags = validated_data.pop("tags", None)
        nutrition = validated_data.pop("nutrition", None)
        additive = validated_data.pop("additive", None)
        percent_data = validated_data.pop("percentData", None)

        # 更新基本字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # 处理百分比数据
        if percent_data is not None:
            for key, value in percent_data.items():
                setattr(instance, key, value)

        instance.save()

        # 更新标签
        if tags is not None:
            # 删除旧标签关系
            instance.tag_relations.all().delete()
            self._handle_tags(instance, tags)

        # 更新营养成分
        if nutrition is not None:
            instance.ingredients.all().delete()
            self._handle_nutrition(instance, nutrition)

        # 更新添加剂
        if additive is not None:
            instance.additives.all().delete()
            self._handle_additives(instance, additive)

        return instance

    def _handle_tags(self, catfood, tag_names):
        """处理标签"""
        for tag_name in tag_names:
            tag, _ = CatFoodTag.objects.get_or_create(name=tag_name)
            CatFoodTagRelation.objects.create(catfood=catfood, tag=tag)

    def _handle_nutrition(self, catfood, ingredient_ids):
        """处理营养成分"""
        for order, ingredient_id in enumerate(ingredient_ids):
            try:
                ingredient = Ingredient.objects.get(id=ingredient_id)
                CatFoodIngredient.objects.create(
                    catfood=catfood, ingredient=ingredient, order=order
                )
            except Ingredient.DoesNotExist:
                pass

    def _handle_additives(self, catfood, additive_ids):
        """处理添加剂"""
        for order, additive_id in enumerate(additive_ids):
            try:
                additive = Additive.objects.get(id=additive_id)
                CatFoodAdditive.objects.create(catfood=catfood, additive=additive, order=order)
            except Additive.DoesNotExist:
                pass
