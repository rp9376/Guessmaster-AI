from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging

from .utils import OllamaGameEngine, GameSessionManager
from .models import GameSession

logger = logging.getLogger(__name__)


class GameView(View):
    """
    Main game view for rendering the game interface
    """
    
    def get(self, request):
        """Render the game page"""
        # Get or create game session
        game_session = GameSessionManager.get_or_create_session(request)
        
        context = {
            'session_id': str(game_session.session_id),
            'question_count': game_session.question_count,
            'conversation_history': game_session.conversation_history,
            'is_completed': game_session.is_completed,
            'max_questions': 20
        }
        
        return render(request, 'game/game.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class AskQuestionView(View):
    """
    API endpoint for asking questions to the AI
    """
    
    def post(self, request):
        """Handle question submission"""
        try:
            # Parse request body
            data = json.loads(request.body)
            question = data.get('question', '').strip()
            
            if not question:
                return JsonResponse({
                    'success': False,
                    'error': 'Question is required'
                }, status=400)
            
            # Get or create game session
            game_session = GameSessionManager.get_or_create_session(request)
            
            # Check if game is already completed
            if game_session.is_completed:
                return JsonResponse({
                    'success': False,
                    'error': 'Game is already completed. Please reset to start a new game.'
                }, status=400)
            
            # Check if max questions reached
            if game_session.question_count >= 20:
                return JsonResponse({
                    'success': False,
                    'error': 'Maximum questions reached. Please reset to start a new game.'
                }, status=400)
            
            # Initialize game engine
            game_engine = OllamaGameEngine()
            
            # Validate question
            validation_result = game_engine.validate_question(question)
            if not validation_result['valid']:
                return JsonResponse({
                    'success': False,
                    'error': validation_result['error']
                }, status=400)
            
            # Get conversation context
            conversation_context = game_session.get_conversation_context()
            
            # Get AI response
            ai_result = game_engine.get_ai_response(conversation_context, question)
            
            if not ai_result['success']:
                return JsonResponse({
                    'success': False,
                    'error': ai_result['error'],
                    'details': ai_result.get('details', '')
                }, status=500)
            
            ai_response = ai_result['response']
            
            # Add question and answer to session
            game_session.add_question_answer(question, ai_response)
            
            # Check if game should be completed
            if game_session.question_count >= 20:
                game_session.is_completed = True
                game_session.save()
            
            return JsonResponse({
                'success': True,
                'response': ai_response,
                'question_count': game_session.question_count,
                'max_questions': 20,
                'is_completed': game_session.is_completed,
                'session_id': str(game_session.session_id)
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON in request body'
            }, status=400)
        except Exception as e:
            logger.error(f"Error in AskQuestionView: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'An unexpected error occurred'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ResetGameView(View):
    """
    API endpoint for resetting the game session
    """
    
    def post(self, request):
        """Handle game reset"""
        try:
            # Reset game session
            game_session = GameSessionManager.reset_session(request)
            
            return JsonResponse({
                'success': True,
                'message': 'Game reset successfully',
                'session_id': str(game_session.session_id),
                'question_count': game_session.question_count,
                'is_completed': game_session.is_completed
            })
            
        except Exception as e:
            logger.error(f"Error in ResetGameView: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to reset game'
            }, status=500)


# Function-based views for backward compatibility
@csrf_exempt
@require_http_methods(["POST"])
def ask_question(request):
    """Function-based view wrapper for AskQuestionView"""
    view = AskQuestionView()
    return view.post(request)


@csrf_exempt
@require_http_methods(["POST"])
def reset_game(request):
    """Function-based view wrapper for ResetGameView"""
    view = ResetGameView()
    return view.post(request)
