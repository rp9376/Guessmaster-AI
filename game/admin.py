from django.contrib import admin
from .models import GameSession


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'question_count', 'is_completed', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_completed', 'is_active', 'created_at']
    search_fields = ['session_id']
    readonly_fields = ['session_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Session Info', {
            'fields': ('session_id', 'created_at', 'updated_at')
        }),
        ('Game Status', {
            'fields': ('is_active', 'is_completed', 'question_count')
        }),
        ('Conversation', {
            'fields': ('conversation_history',),
            'classes': ('collapse',)
        }),
    )
