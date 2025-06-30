import requests
import json
import logging
from django.conf import settings
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class OllamaGameEngine:
    """
    Game engine for handling communication with Ollama AI
    """
    
    def __init__(self):
        self.ollama_url = settings.OLLAMA_URL
        self.model_name = settings.OLLAMA_MODEL
        
    def get_ai_response(self, conversation_context: str, user_question: str) -> Dict[str, Any]:
        """
        Send question to Ollama and get AI response
        
        Args:
            conversation_context: Previous conversation history
            user_question: Current user question
            
        Returns:
            Dict containing success status and response/error
        """
        try:
            # Prepare the prompt for the AI
            prompt = self._prepare_prompt(conversation_context, user_question)
            
            # Make request to Ollama
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 150
                }
            }
            
            response = requests.post(
                self.ollama_url,
                json=payload,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                response_data = response.json()
                ai_response = response_data.get('response', '').strip()
                
                return {
                    'success': True,
                    'response': ai_response,
                    'raw_response': response_data
                }
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"API Error: {response.status_code}",
                    'details': response.text
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request to Ollama failed: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to connect to AI service',
                'details': str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error in get_ai_response: {str(e)}")
            return {
                'success': False,
                'error': 'Unexpected error occurred',
                'details': str(e)
            }
    
    def _prepare_prompt(self, conversation_context: str, user_question: str) -> str:
        """
        Prepare the prompt for the AI model
        
        Args:
            conversation_context: Previous conversation history
            user_question: Current user question
            
        Returns:
            Formatted prompt string
        """
        system_prompt = """You are playing a 20 questions game. You are thinking of a specific object, person, place, or concept, and the human player is trying to guess what it is by asking yes/no questions.

Rules:
1. Only answer with "Yes", "No", or "Sometimes/Partially" (if the answer isn't clearly yes or no)
2. Be consistent with your chosen answer throughout the game
3. Keep your responses brief and clear
4. If asked to guess or if the player makes a direct guess, confirm if they're correct
5. If they reach 20 questions without guessing, reveal your answer

"""
        
        full_prompt = f"{system_prompt}\n\n{conversation_context}\n\nHuman: {user_question}\n\nAI:"
        
        return full_prompt
    
    def validate_question(self, question: str) -> Dict[str, Any]:
        """
        Validate if the question is appropriate for the game
        
        Args:
            question: User's question
            
        Returns:
            Dict with validation result
        """
        if not question or len(question.strip()) < 3:
            return {
                'valid': False,
                'error': 'Question is too short'
            }
        
        if len(question) > 500:
            return {
                'valid': False,
                'error': 'Question is too long (max 500 characters)'
            }
        
        # Check for inappropriate content (basic filtering)
        inappropriate_words = ['fuck', 'shit', 'damn', 'hell']  # Add more as needed
        if any(word in question.lower() for word in inappropriate_words):
            return {
                'valid': False,
                'error': 'Please keep questions appropriate'
            }
        
        return {
            'valid': True
        }


class GameSessionManager:
    """
    Manager for handling game session operations
    """
    
    @staticmethod
    def get_or_create_session(request) -> 'GameSession':
        """
        Get existing session or create new one
        
        Args:
            request: Django request object
            
        Returns:
            GameSession instance
        """
        from .models import GameSession
        
        session_id = request.session.get('game_session_id')
        
        if session_id:
            try:
                game_session = GameSession.objects.get(
                    session_id=session_id,
                    is_active=True
                )
                return game_session
            except GameSession.DoesNotExist:
                pass
        
        # Create new session
        game_session = GameSession.objects.create()
        request.session['game_session_id'] = str(game_session.session_id)
        
        return game_session
    
    @staticmethod
    def reset_session(request) -> 'GameSession':
        """
        Reset current session or create new one
        
        Args:
            request: Django request object
            
        Returns:
            GameSession instance
        """
        from .models import GameSession
        
        session_id = request.session.get('game_session_id')
        
        if session_id:
            try:
                game_session = GameSession.objects.get(session_id=session_id)
                game_session.reset_session()
                return game_session
            except GameSession.DoesNotExist:
                pass
        
        # Create new session
        game_session = GameSession.objects.create()
        request.session['game_session_id'] = str(game_session.session_id)
        
        return game_session
