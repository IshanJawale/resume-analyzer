from django.contrib import admin
from .models import ResumeAnalysis, UserProfile, AnalysisRecommendation

@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ['user', 'filename', 'overall_score', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'overall_score']
    search_fields = ['user__username', 'filename']
    readonly_fields = ['created_at', 'updated_at', 'analyzed_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'filename', 'file', 'status')
        }),
        ('Scores', {
            'fields': ('overall_score', 'content_score', 'formatting_score', 'keywords_score', 'experience_score')
        }),
        ('Analysis Details', {
            'fields': ('summary', 'strengths', 'weaknesses', 'recommendations')
        }),
        ('Keywords', {
            'fields': ('found_keywords', 'missing_keywords')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'analyzed_at')
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_analyses', 'email_notifications', 'created_at']
    list_filter = ['email_notifications', 'marketing_emails', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(AnalysisRecommendation)
class AnalysisRecommendationAdmin(admin.ModelAdmin):
    list_display = ['analysis', 'title', 'priority', 'category']
    list_filter = ['priority', 'category']
    search_fields = ['title', 'description']
