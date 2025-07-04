# GuessMaster 20Q - AI vs Human

A stateless Django web application for playing 20 Questions against an AI powered by Ollama and LLaMA.

## Features

- **Stateless Architecture**: No database or session storage required
- **Real-time Streaming**: AI responses stream in real-time to the frontend
- **Privacy-Conscious**: All AI communication goes through the backend
- **Multi-user Support**: Multiple users can play simultaneously without interference
- **Debug Console**: Full prompt logging in browser console for debugging
- **Modern UI**: Beautiful, responsive interface with Tailwind CSS

## Quick Start

```bash
# 1. Copy environment template
cp .env.template .env

# 2. Edit .env with your Ollama settings
nano .env

# 3. Run with Docker (recommended)
docker-compose up --build -d

# OR run locally
./setup.sh
python3 manage.py runserver 9090
```

## Prerequisites

- Python 3.11+
- **Ollama with LLaMA model already installed and running**
- Docker (optional, for containerized deployment)

## Quick Start

### Option 1: Local Development

**Quick Setup:**
```bash
./setup.sh
# Follow the instructions printed by the setup script
```

**Manual Setup:**

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   # Copy the template and edit with your settings
   cp .env.template .env
   # Edit .env with your Ollama configuration
   # Point OLLAMA_URL to your existing Ollama instance
   ```

3. **Ensure Ollama is running** with your desired model:
   ```bash
   # Verify Ollama is accessible
   curl http://your-ollama-host:11434/api/tags
   ```

4. **Run Django server**:
   ```bash
   python manage.py runserver 9090
   ```

5. **Open browser**: http://localhost:9090

### Option 2: Docker

**Prerequisites**: Ensure your Ollama instance is accessible from Docker containers.

1. **Configure Ollama URL**: Copy the environment template and configure it:
   ```bash
   cp .env.template .env
   # Edit .env with your Ollama configuration
   ```
   
   Example configurations:
   ```bash
   # For Ollama running on host system (from Docker container perspective)
   OLLAMA_URL=http://host.docker.internal:11434/api/generate
   # OR for remote Ollama instance
   OLLAMA_URL=http://your-ollama-server:11434/api/generate
   ```

2. **Start the web service**:
   ```bash
   docker-compose up --build -d
   ```
   
   The container will automatically restart unless manually stopped.

3. **Open browser**: http://localhost:9090

## How It Works

### Game Flow
1. User visits the homepage and clicks "Start Game"
2. Frontend sends conversation history to `/api/ask/` endpoint
3. Backend loads system prompt from `llm_prompt.txt`
4. Backend sends full prompt (system + history) to Ollama
5. AI response streams back to frontend in real-time
6. Process repeats for up to 20 questions

### Architecture
- **Frontend**: Vanilla JavaScript with fetch API for streaming
- **Backend**: Django with stateless API endpoint
- **AI**: Ollama serving LLaMA model locally
- **State Management**: All game state managed in frontend JavaScript

### API Endpoint

**POST** `/api/ask/`

Request body:
```json
{
  "history": [
    {"role": "assistant", "content": "Is it alive?"},
    {"role": "user", "content": "Yes"},
    ...
  ]
}
```

Response: Server-Sent Events stream with AI response

## Configuration

### Environment Template

The project includes a `.env.template` file with all configuration options and examples. To set up your environment:

```bash
# Copy the template
cp .env.template .env

# Edit .env with your specific settings
nano .env  # or use your preferred editor
```

### Environment Variables (.env)
```
OLLAMA_URL=http://your-ollama-host:11434/api/generate
OLLAMA_MODEL=llama3.2
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
SECRET_KEY=your-secret-key-here
WEB_PORT=9090
```

**Note**: Replace `your-ollama-host` with the actual hostname/IP where your Ollama instance is running.

### System Prompt
Edit `game/llm_prompt.txt` to customize the AI's behavior and strategy.

## Project Structure

```
project_root/
├── manage.py
├── .env
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── game/
│   ├── views.py           # API endpoint logic
│   ├── urls.py
│   ├── llm_prompt.txt     # AI system instructions
│   ├── templates/game/
│   │   └── index.html     # Main game interface  
│   └── static/js/
│       └── game.js        # Frontend game logic
└── project/
    ├── settings.py        # Django configuration
    └── urls.py
```

## Privacy & Security

- No user data stored on server
- All game state managed client-side
- AI communication proxied through backend
- CORS configured for development
- Input validation and sanitization

## Debugging

The full prompt sent to the LLM is logged in the browser console for debugging purposes. Open browser dev tools (F12) to view:

```javascript
console.log('🔍 DEBUG - Full prompt sent to LLM:', prompt);
```

## Customization

### Modify AI Behavior
Edit `game/llm_prompt.txt` to change the AI's strategy and personality.

### Styling
The UI uses Tailwind CSS. Modify `game/templates/game/index.html` to customize appearance.

### AI Model
Change `OLLAMA_MODEL` in `.env` to use different models (requires model to be pulled first).

## Troubleshooting

### Common Issues

1. **Ollama connection error**: 
   - Ensure your Ollama instance is running and accessible
   - Check the OLLAMA_URL in your .env file
   - Test connectivity: `curl http://your-ollama-host:11434/api/tags`
2. **Model not found**: Ensure your specified model is available in your Ollama instance
3. **Port conflicts**: Change ports in docker-compose.yml if needed
4. **CORS errors**: Check ALLOWED_HOSTS in settings
5. **Docker networking**: If using Docker, make sure Ollama is accessible from containers

### Development Tips

- Check browser console for debug logs
- Monitor Django console for backend errors
- Use `docker-compose logs` for container debugging
- **Test Ollama connectivity**: Visit http://localhost:9090/api/test-ollama/ to verify your Ollama connection

## License

MIT License - feel free to modify and distribute.
