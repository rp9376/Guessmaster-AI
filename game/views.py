import json
import os
import requests
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings


def index(request):
    """Serve the main game page."""
    return render(request, 'game/index.html')


@csrf_exempt
@require_http_methods(["POST"])
def ask_ai(request):
    """
    Handle AI conversation requests.
    Accepts conversation history and returns AI response.
    """
    try:
        # Parse request data
        data = json.loads(request.body)
        history = data.get('history', [])
        
        # Validate history format
        if not isinstance(history, list):
            return JsonResponse({'error': 'History must be an array'}, status=400)
        
        # Load system prompt
        prompt_path = os.path.join(os.path.dirname(__file__), 'llm_prompt.txt')
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                system_prompt = f.read().strip()
        except FileNotFoundError:
            return JsonResponse({'error': 'System prompt file not found'}, status=500)
        
        # Build full conversation for Ollama
        # Combine system prompt and conversation history into a single prompt
        full_prompt = system_prompt + "\n\n"
        
        for msg in history:
            if msg['role'] == 'assistant':
                full_prompt += f"AI: {msg['content']}\n"
            elif msg['role'] == 'user':
                full_prompt += f"Human: {msg['content']}\n"
        
        # Add the current question prompt
        full_prompt += "AI: "
        
        # Prepare Ollama request for /api/generate endpoint
        ollama_data = {
            "model": settings.OLLAMA_MODEL,
            "prompt": full_prompt,
            "stream": True,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
            }
        }
        
        # DEBUG: Print the request details to console
        print("\n" + "="*60)
        print("🔍 DEBUG: Ollama Request Details")
        print("="*60)
        print(f"URL: {settings.OLLAMA_URL}")
        print(f"Model: {settings.OLLAMA_MODEL}")
        print(f"Full Prompt:\n{full_prompt}")
        print(f"Request Data: {json.dumps(ollama_data, indent=2)}")
        print("="*60 + "\n")
        
        # Make request to Ollama
        try:
            response = requests.post(
                settings.OLLAMA_URL,  # Use the URL directly (already points to /api/generate)
                json=ollama_data,
                stream=True,
                timeout=30
            )
            response.raise_for_status()
            print(f"✅ Successfully connected to Ollama. Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ ERROR: Failed to connect to Ollama: {str(e)}")
            print(f"Response status: {getattr(e.response, 'status_code', 'N/A')}")
            print(f"Response text: {getattr(e.response, 'text', 'N/A')}")
            return JsonResponse({
                'error': f'Failed to connect to Ollama: {str(e)}'
            }, status=500)
        
        # Stream response back to client
        def generate_response():
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        # For /api/generate endpoint, response is in 'response' field
                        if 'response' in chunk:
                            content = chunk['response']
                            full_response += content
                            yield f"data: {json.dumps({'content': content})}\n\n"
                        
                        if chunk.get('done', False):
                            # Send debug info with full prompt
                            debug_info = {
                                'type': 'debug',
                                'full_prompt': full_prompt,
                                'full_response': full_response
                            }
                            yield f"data: {json.dumps(debug_info)}\n\n"
                            yield "data: [DONE]\n\n"
                            break
                    except json.JSONDecodeError:
                        continue
        
        return StreamingHttpResponse(
            generate_response(),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
            }
        )
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)
