from rest_framework import serializers
from .models import Conversation, Message, CodeExecution

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content', 'is_bot', 'created_at']

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'language', 'created_at', 'messages'] 

class CodeExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeExecution
        fields = ['id', 'code', 'output', 'error', 'language', 'executed_at'] 