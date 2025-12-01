from django.contrib import admin
from .models import ReputationSummary, Badge, UserBadge

@admin.register(ReputationSummary)
class ReputationSummaryAdmin(admin.ModelAdmin):
    list_display = ["user", "score", "level", "updated_at"]
    search_fields = ["user__username", "user__email"]
    list_filter = ["level", "updated_at"]
    readonly_fields = ["updated_at", "score", "profile_completeness", "review_quality", "community_contribution", "compliance"]

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "enabled"]
    search_fields = ["code", "name"]
    list_filter = ["enabled"]
    
@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ["user", "badge", "is_equipped", "acquired_at"]
    search_fields = ["user__username", "badge__code", "badge__name"]
    list_filter = ["is_equipped", "acquired_at"]