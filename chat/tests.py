from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Conversation, Message, CodeExecution
from .services import CodeExecutionService
import os

User = get_user_model()

class CodeExecutionServiceTests(TestCase):
    def test_execute_valid_python_code(self):
        code = """
print('Hello, World!')
x = 5 + 3
print(f'Result: {x}')
"""
        service = CodeExecutionService()
        output, error = service.execute_python_code(code)
        
        self.assertIn('Hello, World!', output)
        self.assertIn('Result: 8', output)
        self.assertEqual(error, '')

    def test_execute_code_with_syntax_error(self):
        code = """
print('Hello, World!'
x = 5 + 
"""
        service = CodeExecutionService()
        output, error = service.execute_python_code(code)
        
        self.assertEqual(output, '')
        self.assertNotEqual(error, '')

    def test_execute_code_with_timeout(self):
        code = """
while True:
    pass
"""
        service = CodeExecutionService()
        output, error = service.execute_python_code(code)
        
        self.assertEqual(output, '')
        self.assertIn('timeout', error.lower())

class ChatViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.conversation = Conversation.objects.create(
            user=self.user,
            title='Test Conversation',
            language='both'
        )
        os.environ['OPENAI_API_KEY'] = 'test_key'

    def test_execute_code_endpoint(self):
        url = f'/api/conversations/{self.conversation.id}/execute_code/'
        data = {
            'code': 'print("Hello, Test!")',
            'language': 'python'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Hello, Test!', response.data['output'])
        
        # Check if CodeExecution was created
        self.assertTrue(CodeExecution.objects.filter(conversation=self.conversation).exists())

    def test_execute_code_with_persian_error(self):
        url = f'/api/conversations/{self.conversation.id}/execute_code/'
        data = {
            'code': '',  # Empty code should trigger Persian error
            'language': 'python',
            'message': 'تست'  # Persian message to trigger Persian error
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('کد', response.data['error'])

    def test_send_message_with_code_execution(self):
        url = f'/api/conversations/{self.conversation.id}/send_message/'
        data = {
            'message': 'Please run this code: print("Hello from test!")'
        }
        
        self.assertEqual(Message.objects.count(), 0)
        
        try:
            response = self.client.post(url, data, format='json')
            print(f"Response data: {response.data}")  
        except Exception as e:
            print(f"Exception occurred: {str(e)}")  
            raise
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        messages = Message.objects.all().order_by('created_at')
        self.assertEqual(messages.count(), 2)  
        
        user_message = messages.first()
        self.assertFalse(user_message.is_bot)
        self.assertEqual(user_message.content, data['message'])
        
        bot_message = messages.last()
        self.assertTrue(bot_message.is_bot)

class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.conversation = Conversation.objects.create(
            user=self.user,
            title='Test Conversation',
            language='both'
        )

    def test_code_execution_str_method(self):
        code_execution = CodeExecution.objects.create(
            conversation=self.conversation,
            code='print("test")',
            output='test',
            language='python'
        )
        expected_str = f"Code Execution - {self.conversation.title}"
        self.assertEqual(str(code_execution), expected_str)

    def test_conversation_str_method(self):
        expected_str = f"{self.conversation.title} - {self.user.username}"
        self.assertEqual(str(self.conversation), expected_str)

    def test_message_str_method(self):
        message = Message.objects.create(
            conversation=self.conversation,
            content='Test message',
            is_bot=False
        )
        expected_str = f"User: Test message"
        self.assertEqual(str(message), expected_str)
