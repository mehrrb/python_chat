from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
import openai
from django.conf import settings
import os

class PromptManager:
    @staticmethod
    def get_system_prompt():
        return """You are a Python and Django expert who can communicate fluently in both Persian (Farsi) and English.
        When responding:
        1. If the question is in Persian, respond in Persian
        2. If the question is in English, respond in English
        3. For code examples, always include comments in both Persian and English
        4. Focus on Python, Django, and DRF related answers
        5. Keep explanations clear and practical
        
        Remember:
        - Use proper Persian technical terms
        - Explain complex concepts in simple terms
        - Include relevant code examples when needed
        """

class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['POST'])
    def send_message(self, request, pk=None):
        conversation = self.get_object()
        user_message = request.data.get('message')
        
        if not user_message:
            return Response(
                {'error': 'Message is required' if not self._is_persian(user_message) else 'پیام نمی‌تواند خالی باشد'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        Message.objects.create(
            conversation=conversation,
            content=user_message,
            is_bot=False
        )

        try:
            client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": PromptManager.get_system_prompt()},
                    {"role": "user", "content": user_message}
                ]
            )

            bot_response = response.choices[0].message.content

            bot_message = Message.objects.create(
                conversation=conversation,
                content=bot_response,
                is_bot=True
            )

            return Response({
                'message': MessageSerializer(bot_message).data
            })

        except Exception as e:
            error_message = 'Server error' if not self._is_persian(user_message) else 'خطا در ارتباط با سرور'
            return Response(
                {'error': f"{error_message}: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['GET'])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        messages = conversation.messages.all().order_by('created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @staticmethod
    def _is_persian(text):
        """Check if the text is in Persian"""
        persian_chars = set('ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی')
        text_chars = set(text)
        return bool(persian_chars & text_chars)
