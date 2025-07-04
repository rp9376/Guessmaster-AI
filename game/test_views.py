import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


@csrf_exempt
def test_ollama(request):
    """
    Test endpoint to verify Ollama connectivity.
    GET /api/test-ollama/
    """
    try:
        # Test basic connectivity to Ollama
        test_url = settings.OLLAMA_URL.replace('/api/generate', '/api/tags')
        
        response = requests.get(test_url, timeout=10)
        response.raise_for_status()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Ollama is accessible',
            'ollama_url': settings.OLLAMA_URL,
            'model': settings.OLLAMA_MODEL,
            'available_models': response.json().get('models', [])
        })
        
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Cannot connect to Ollama: {str(e)}',
            'ollama_url': settings.OLLAMA_URL,
            'model': settings.OLLAMA_MODEL
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Unexpected error: {str(e)}'
        }, status=500)
