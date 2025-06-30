from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
import json

from .models import GameSession
from .utils import OllamaGameEngine, GameSessionManager


class GameSessionModelTest(TestCase):
    """Test GameSession model functionality"""
    
    def setUp(self):
        self.session = GameSession.objects.create()
    
    def test_game_session_creation(self):
        """Test that GameSession is created with default values"""
        self.assertIsNotNone(self.session.session_id)
        self.assertEqual(self.session.question_count, 0)
        self.assertEqual(self.session.conversation_history, [])
        self.assertTrue(self.session.is_active)
        self.assertFalse(self.session.is_completed)
    
    def test_add_question_answer(self):
        """Test adding question-answer pairs"""
        question = "Is it an animal?"
        answer = "Yes"
        
        self.session.add_question_answer(question, answer)
        
        self.assertEqual(self.session.question_count, 1)
        self.assertEqual(len(self.session.conversation_history), 1)
        self.assertEqual(self.session.conversation_history[0]['question'], question)
        self.assertEqual(self.session.conversation_history[0]['answer'], answer)
    
    def test_get_conversation_context(self):
        """Test conversation context generation"""
        # Test empty conversation
        context = self.session.get_conversation_context()
        self.assertIn("20 questions game", context)
        
        # Test with conversation history
        self.session.add_question_answer("Is it alive?", "No")
        self.session.add_question_answer("Is it man-made?", "Yes")
        
        context = self.session.get_conversation_context()
        self.assertIn("Q1: Is it alive?", context)
        self.assertIn("A1: No", context)
        self.assertIn("Q2: Is it man-made?", context)
        self.assertIn("A2: Yes", context)
    
    def test_reset_session(self):
        """Test session reset functionality"""
        # Add some data
        self.session.add_question_answer("Test question", "Test answer")
        self.session.is_completed = True
        self.session.save()
        
        # Reset
        self.session.reset_session()
        
        self.assertEqual(self.session.question_count, 0)
        self.assertEqual(self.session.conversation_history, [])
        self.assertFalse(self.session.is_completed)
        self.assertTrue(self.session.is_active)


class OllamaGameEngineTest(TestCase):
    """Test OllamaGameEngine functionality"""
    
    def setUp(self):
        self.engine = OllamaGameEngine()
    
    def test_validate_question_valid(self):
        """Test question validation with valid input"""
        result = self.engine.validate_question("Is it red?")
        self.assertTrue(result['valid'])
    
    def test_validate_question_too_short(self):
        """Test question validation with too short input"""
        result = self.engine.validate_question("No")
        self.assertFalse(result['valid'])
        self.assertIn("too short", result['error'])
    
    def test_validate_question_too_long(self):
        """Test question validation with too long input"""
        long_question = "A" * 501
        result = self.engine.validate_question(long_question)
        self.assertFalse(result['valid'])
        self.assertIn("too long", result['error'])
    
    def test_prepare_prompt(self):
        """Test prompt preparation"""
        context = "Previous conversation context"
        question = "Is it blue?"
        
        prompt = self.engine._prepare_prompt(context, question)
        
        self.assertIn("20 questions game", prompt)
        self.assertIn(context, prompt)
        self.assertIn(question, prompt)
        self.assertIn("Human:", prompt)
        self.assertIn("AI:", prompt)
    
    @patch('requests.post')
    def test_get_ai_response_success(self, mock_post):
        """Test successful AI response"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'response': 'Yes, it is blue.'
        }
        mock_post.return_value = mock_response
        
        result = self.engine.get_ai_response("Context", "Is it blue?")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['response'], 'Yes, it is blue.')
    
    @patch('requests.post')
    def test_get_ai_response_failure(self, mock_post):
        """Test failed AI response"""
        # Mock failed response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        result = self.engine.get_ai_response("Context", "Is it blue?")
        
        self.assertFalse(result['success'])
        self.assertIn("API Error", result['error'])


class GameViewsTest(TestCase):
    """Test game views"""
    
    def setUp(self):
        self.client = Client()
    
    def test_game_view_get(self):
        """Test GET request to game view"""
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Guessmaster AI')
    
    def test_ask_question_without_session(self):
        """Test asking question without existing session"""
        data = {'question': 'Is it red?'}
        response = self.client.post('/ask/', 
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        # Should create new session and process question
        self.assertEqual(response.status_code, 500)  # Will fail due to Ollama connection
        
        # Check that session was created
        self.assertTrue(GameSession.objects.exists())
    
    def test_ask_question_invalid_json(self):
        """Test asking question with invalid JSON"""
        response = self.client.post('/ask/', 
                                   data='invalid json',
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('Invalid JSON', data['error'])
    
    def test_ask_question_empty_question(self):
        """Test asking empty question"""
        data = {'question': ''}
        response = self.client.post('/ask/', 
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('required', data['error'])
    
    def test_reset_game(self):
        """Test game reset"""
        # Create a session first
        session = GameSession.objects.create()
        session.add_question_answer("Test", "Test")
        
        # Set session in client
        client_session = self.client.session
        client_session['game_session_id'] = str(session.session_id)
        client_session.save()
        
        response = self.client.post('/reset/', 
                                   data=json.dumps({}),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Check that session was reset
        session.refresh_from_db()
        self.assertEqual(session.question_count, 0)


class GameSessionManagerTest(TestCase):
    """Test GameSessionManager functionality"""
    
    def setUp(self):
        self.client = Client()
    
    def test_get_or_create_session_new(self):
        """Test creating new session when none exists"""
        request = self.client.get('/').wsgi_request
        
        session = GameSessionManager.get_or_create_session(request)
        
        self.assertIsNotNone(session)
        self.assertEqual(session.question_count, 0)
        self.assertTrue(session.is_active)
    
    def test_get_or_create_session_existing(self):
        """Test getting existing session"""
        # Create initial session
        request = self.client.get('/').wsgi_request
        session1 = GameSessionManager.get_or_create_session(request)
        
        # Get same session
        session2 = GameSessionManager.get_or_create_session(request)
        
        self.assertEqual(session1.session_id, session2.session_id)
    
    def test_reset_session(self):
        """Test session reset"""
        request = self.client.get('/').wsgi_request
        
        # Create session with data
        session = GameSessionManager.get_or_create_session(request)
        session.add_question_answer("Test", "Test")
        
        # Reset session
        reset_session = GameSessionManager.reset_session(request)
        
        self.assertEqual(reset_session.session_id, session.session_id)
        self.assertEqual(reset_session.question_count, 0)
        self.assertEqual(reset_session.conversation_history, [])
