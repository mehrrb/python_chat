from django.contrib import admin
from .models import Conversation, Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'content_preview', 'is_bot', 'created_at')
    list_filter = ('is_bot', 'created_at')
    search_fields = ('content', 'conversation__title')
    readonly_fields = ('created_at',)

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'message_count')
    list_filter = ('created_at', 'user')
    search_fields = ('title', 'user__username')
    readonly_fields = ('created_at',)

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Number of Messages'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
