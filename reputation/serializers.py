from rest_framework import serializers
from .models import ReputationSummary, Badge, UserBadge

class ReputationSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReputationSummary
        fields = ["score", "profile_completeness", "review_quality", "community_contribution", "compliance", "level", "updated_at"]

class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ["code", "name", "description", "icon", "enabled", "rule"]
        
class UserBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)

    class Meta:
        model = UserBadge
        fields = ["badge", "is_equipped", "acquired_at"]