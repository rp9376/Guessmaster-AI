# 🎯 Guessmaster AI - 20 Questions Game

A web-based 20 Questions game where humans compete against an AI powered by Ollama running a LLaMA model. The AI thinks of something, and you have 20 questions to guess what it is!

## Features

- 🤖 AI-powered responses using Ollama and LLaMA
- 💬 Session-based conversation history
- 🎯 Classic 20 questions gameplay
- 🌐 Modern web interface
- 🐳 Docker containerized deployment
- 📊 PostgreSQL database for session storage
- 🔄 Game reset functionality
- 📱 Mobile-responsive design

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Ollama running locally with LLaMA model

### 1. Set up Ollama

First, install and run Ollama with a LLaMA model:

```bash
# Install Ollama (visit https://ollama.ai for installation instructions)

# Pull a model (e.g., llama3)
ollama pull llama3

# Start Ollama server (usually runs on localhost:11434)
ollama serve
```

### 2. Clone and Configure

```bash
git clone <your-repo-url>
cd Guessmaster-AI

# Copy and edit environment variables
cp .env.example .env
# Edit .env file with your settings
```

### 3. Run with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

The application will be available at:
- **Game**: http://localhost:8000
- **Admin**: http://localhost:8000/admin
- **PgAdmin**: http://localhost:5050

## Manual Setup (Without Docker)

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Set up Database

```bash
# Install PostgreSQL locally or use SQLite for development
# Edit .env file for database settings

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 3. Run Development Server

```bash
# Collect static files
python manage.py collectstatic

# Run development server
python manage.py runserver
```

## Configuration

### Environment Variables (.env)

```env
# Ollama Configuration
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3

# Django Configuration
DEBUG=True
SECRET_KEY=your-secret-key-change-this-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_URL=postgres://user:password@db:5432/guessmaster
POSTGRES_DB=guessmaster
POSTGRES_USER=user
POSTGRES_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
```

## API Endpoints

### POST /ask/
Ask a question to the AI.

**Request:**
```json
{
    "question": "Is it alive?"
}
```

**Response:**
```json
{
    "success": true,
    "response": "No, it is not alive.",
    "question_count": 1,
    "max_questions": 20,
    "is_completed": false,
    "session_id": "uuid-here"
}
```

### POST /reset/
Reset the current game session.

**Response:**
```json
{
    "success": true,
    "message": "Game reset successfully",
    "session_id": "new-uuid-here",
    "question_count": 0,
    "is_completed": false
}
```

## Project Structure

```
Guessmaster-AI/
├── game/                   # Django app
│   ├── models.py          # GameSession model
│   ├── views.py           # API views
│   ├── utils.py           # Game engine and utilities
│   ├── urls.py            # URL routing
│   ├── admin.py           # Django admin configuration
│   ├── tests.py           # Unit tests
│   └── templates/         # HTML templates
│       └── game/
│           └── game.html  # Main game interface
├── project/               # Django project settings
│   ├── settings.py        # Configuration
│   ├── urls.py            # Root URL routing
│   ├── wsgi.py           # WSGI configuration
│   └── asgi.py           # ASGI configuration
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Multi-container setup
├── .env                  # Environment variables
└── README.md             # This file
```

## Game Logic

1. **Session Management**: Each user gets a unique session to track their game
2. **AI Integration**: Questions are sent to Ollama with full conversation context
3. **Question Tracking**: System tracks question count and enforces 20-question limit
4. **Conversation History**: Full Q&A history is maintained and sent to AI for context
5. **Game Reset**: Users can start new games at any time

## Development

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test game

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

### Admin Interface

Create a superuser to access the Django admin:

```bash
python manage.py createsuperuser
```

Then visit http://localhost:8000/admin to manage game sessions.

## Troubleshooting

### Ollama Connection Issues

1. Ensure Ollama is running: `ollama serve`
2. Check if model is available: `ollama list`
3. Test API directly:
   ```bash
   curl -X POST http://localhost:11434/api/generate \
        -H "Content-Type: application/json" \
        -d '{"model": "llama3", "prompt": "Hello", "stream": false}'
   ```

### Docker Issues

1. Check if containers are running: `docker-compose ps`
2. View logs: `docker-compose logs web`
3. Rebuild containers: `docker-compose up --build --force-recreate`

### Database Issues

1. Check database connection in Django admin
2. Run migrations: `python manage.py migrate`
3. Check PostgreSQL logs: `docker-compose logs db`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Django and PostgreSQL
- AI powered by Ollama and LLaMA
- Modern UI with vanilla JavaScript and CSS