# Auto Email Responder

An intelligent email response system that retrieves company policies and generates appropriate responses using Gmail API and LangChain v0.3.

## Features

- **Gmail Integration**: Send and receive emails using Gmail API
- **Intelligent Response Generation**: AI-powered email responses using OpenAI GPT
- **Company Policy Management**: Store and retrieve company policies, FAQs, and templates
- **Semantic Search**: Find relevant policies using vector embeddings (FAISS)
- **Batch Processing**: Process multiple emails efficiently with prompt caching
- **Redis Caching**: Cache frequently accessed policies and responses
- **Background Tasks**: Asynchronous inbox processing
- **RESTful API**: Complete FastAPI-based REST API

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **LangChain v0.3**: Framework for developing applications with LLMs
- **OpenAI GPT**: Language model for generating intelligent responses
- **Gmail API**: Google's API for email operations
- **FAISS**: Vector database for semantic search
- **Redis**: In-memory caching and session storage
- **Pydantic**: Data validation and settings management

## Project Structure

```
auto-email-responder/
├── main.py                     # FastAPI application entry point
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose configuration
├── .env.example               # Environment variables example
├── config/
│   └── settings.py            # Application settings
├── services/
│   ├── gmail_service.py       # Gmail API integration
│   ├── policy_service.py      # Company policies management
│   ├── response_generator.py  # AI response generation
│   └── cache_service.py       # Redis caching service
├── frontend/                  # Frontend application
│   ├── index.html             # Main HTML file
│   ├── api.js                 # API integration
│   ├── app.js                 # UI interactions
│   ├── server.js              # Simple Express server
│   └── package.json           # Frontend dependencies
└── tests/                     # Test files
```

## Prerequisites

- Python 3.11+
- Redis server
- Gmail API credentials
- OpenAI API key

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/auto-email-responder.git
cd auto-email-responder
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` file with your configuration:

```bash
# Gmail API Configuration
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.json

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///./auto_responder.db

# Redis Configuration
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600

# Email Processing Configuration
MAX_BATCH_SIZE=10
PROCESSING_DELAY=2
```

### 5. Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API
4. Create credentials (OAuth 2.0 Client ID)
5. Download the credentials and save as `credentials.json`
6. Run the application once to generate `token.json`

### 6. Start Redis Server

```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or install locally
redis-server
```

## Usage

### Quick Start (Recommended)

For Windows users:
```bash
# Run the batch file to start both servers
start_servers.bat
```

For Linux/Mac users:
```bash
# Run the shell script to start both servers
./start_servers.sh
```

### Manual Start

#### Start the Backend Application

```bash
# Development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Start the Frontend Application

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the frontend server
npm start
```

The frontend will be available at http://localhost:3000

### Troubleshooting Connection Issues

If you see "ERR_CONNECTION_REFUSED" or "Server Disconnected" errors:

1. **Make sure the backend server is running first**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Check if the backend is accessible**:
   - Visit http://localhost:8000/health in your browser
   - You should see a health check response

3. **Verify Redis is running** (if using caching):
   ```bash
   # Using Docker
   docker run -d -p 6379:6379 redis:7-alpine
   
   # Or locally
   redis-server
   ```

4. **Check the frontend server status indicator**:
   - The frontend shows a server status indicator in the top-right corner
   - 🟢 Green = Connected
   - 🔴 Red = Disconnected

5. **Common fixes**:
   - Restart both backend and frontend servers
   - Check if ports 8000 and 3000 are available
   - Ensure all dependencies are installed
   - Check the console for detailed error messages

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run individually
docker build -t auto-email-responder .
docker run -p 8000:8000 auto-email-responder
```

### API Documentation

Once running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc

## API Endpoints

### Email Operations

- `POST /emails/send` - Send single email with AI response
- `POST /emails/batch` - Send multiple emails with batch processing
- `GET /emails/inbox` - Retrieve inbox emails
- `POST /emails/process-inbox` - Process inbox emails with auto-responses

### Policy Management

- `POST /policies/add` - Add new company policy
- `GET /policies/search` - Search for relevant policies
- `GET /policies/all` - Get all company policies

### Cache Management

- `GET /cache/stats` - Get cache statistics
- `POST /cache/clear` - Clear all cached data

### Health Check

- `GET /health` - Application health status

## Example Usage

### Send Email with AI Response

```bash
curl -X POST "http://localhost:8000/emails/send" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "customer@example.com",
    "subject": "Refund Request",
    "body": "I would like to request a refund for my recent purchase",
    "priority": "high"
  }'
```

### Add Company Policy

```bash
curl -X POST "http://localhost:8000/policies/add" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Privacy Policy",
    "content": "Our privacy policy explains how we collect and use your data...",
    "category": "legal",
    "keywords": ["privacy", "data", "gdpr"]
  }'
```

### Search Policies

```bash
curl -X GET "http://localhost:8000/policies/search?query=refund%20policy"
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GMAIL_CREDENTIALS_PATH` | Path to Gmail API credentials | `credentials.json` |
| `GMAIL_TOKEN_PATH` | Path to Gmail API token | `token.json` |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-3.5-turbo` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379` |
| `CACHE_TTL` | Cache time-to-live in seconds | `3600` |
| `MAX_BATCH_SIZE` | Maximum batch size for processing | `10` |
| `PROCESSING_DELAY` | Delay between email processing | `2` |

### Gmail API Scopes

The application requires the following Gmail API scopes:
- `https://www.googleapis.com/auth/gmail.modify`

## Architecture

### Core Components

1. **Gmail Service**: Handles Gmail API operations (send, receive, process emails)
2. **Policy Service**: Manages company policies with vector search capabilities
3. **Response Generator**: Uses LangChain and OpenAI to generate intelligent responses
4. **Cache Service**: Redis-based caching for policies and responses
5. **Frontend**: Web-based user interface for interacting with the system

### Data Flow

#### Backend Flow
1. Email received/requested → Gmail Service
2. Content analyzed → Policy Service (semantic search)
3. Relevant policies retrieved → Response Generator
4. AI response generated → Cache Service (optional)
5. Email sent → Gmail Service

#### Frontend Flow
1. User interacts with UI → Frontend
2. API request sent → Backend API
3. Backend processes request → Response returned
4. Response displayed → Frontend UI

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_gmail_service.py

# Run with coverage
pytest --cov=services tests/
```

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t auto-email-responder .

# Run container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e REDIS_URL=redis://host:6379 \
  auto-email-responder
```

### Production Considerations

- Use environment-specific configuration
- Set up proper logging and monitoring
- Configure SSL/TLS for production
- Use production-grade Redis setup
- Implement rate limiting
- Set up health checks and alerts

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Troubleshooting

### Common Issues

1. **Gmail API Authentication Error**
   - Ensure `credentials.json` is properly configured
   - Check Gmail API is enabled in Google Cloud Console
   - Verify OAuth consent screen is configured

2. **Redis Connection Error**
   - Ensure Redis server is running
   - Check Redis URL configuration
   - Verify network connectivity

3. **OpenAI API Error**
   - Verify API key is valid
   - Check API quota and billing
   - Ensure model availability

### Logs

Application logs are available in the console. For production, configure structured logging:

```python
import structlog
logger = structlog.get_logger()
```

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API docs at `/docs`

## Roadmap

- [ ] Support for multiple email providers
- [ ] Advanced email templates
- [ ] Machine learning-based response optimization
- [ ] Multi-language support
- [ ] Enhanced frontend with real-time updates
- [ ] Mobile-responsive design improvements
- [ ] User authentication and role-based access
- [ ] Analytics and reporting dashboard
- [ ] Integration with CRM systems