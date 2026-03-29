# Confluence RAG

A Retrieval-Augmented Generation (RAG) application that integrates with Confluence to provide intelligent chat capabilities over your documentation and knowledge base.

## Features

- **Confluence Integration**: Seamlessly load and index documentation from Confluence
- **Local Document Loading**: Support for local markdown and document files
- **Semantic Search**: Advanced vector-based search using embeddings
- **AI-Powered Chat**: Interactive chat interface with RAG-enhanced responses
- **Content Guardrails**: Safety checks for input validation and content moderation
- **Semantic Caching**: Optimized response retrieval with intelligent caching
- **Multi-turn Conversations**: Manage conversation history and context
- **Real-time Feedback**: User feedback collection for continuous improvement
- **Docker Support**: Easy deployment with Docker and Docker Compose

## Architecture

### Backend
- **Framework**: FastAPI (Python)
- **Core Components**:
  - `graph_rag.py` - Graph-based RAG implementation
  - `embeddings.py` - Vector embeddings and similarity search
  - `llm.py` - LLM integration and prompt management
  - `vector_store.py` - Vector database operations
  - `semantic_cache.py` - Intelligent response caching
  - `guardrail.py` - Content safety and validation

### Frontend
- **Framework**: React + TypeScript with Vite
- **UI Components**: Chat interface, message display, sidebar navigation
- **Styling**: Tailwind CSS with PostCSS
- **State Management**: Custom hooks for chat and theme management

### Data Layer
- **Ingestion**: Confluence loader, local file loader, HTML parser
- **Chunking**: Text splitting and document chunking strategies
- **Storage**: Persistent conversation and vector storage

## Prerequisites

- Python 3.9+ (backend)
- Node.js 16+ (frontend)
- Docker & Docker Compose (for containerized deployment)
- Confluence instance (for documentation integration)

## Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables (create `.env` file):
```env
# LLM Configuration
OPENAI_API_KEY=your_api_key
LLM_MODEL=gpt-4

# Confluence Configuration
CONFLUENCE_URL=https://your-confluence-instance.atlassian.net
CONFLUENCE_USERNAME=your_username
CONFLUENCE_API_TOKEN=your_api_token

# Database Configuration
DATABASE_URL=sqlite:///./app.db

# Vector Store Configuration
VECTOR_STORE_PATH=./vector_store
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure API endpoint (update `src/services/api.ts` if needed):
```typescript
const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000';
```

## Running the Application

### Using Docker Compose (Recommended)

```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:80
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Manual Setup

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Access the application at http://localhost:5173

## API Endpoints

### Chat
- `POST /api/chat/message` - Send a message and get RAG-enhanced response
- `GET /api/conversations` - List all conversations
- `GET /api/conversations/{id}` - Get conversation details

### Ingestion
- `POST /api/ingest/confluence` - Load documents from Confluence
- `POST /api/ingest/local` - Load documents from local files

### Health
- `GET /api/health` - Health check endpoint

### Feedback
- `POST /api/feedback` - Submit user feedback on responses

## Project Structure

```
confluence-rag/
├── backend/
│   ├── app/
│   │   ├── api/           # API route definitions
│   │   ├── core/          # Core RAG and LLM logic
│   │   ├── db/            # Database operations
│   │   ├── ingestion/     # Document ingestion
│   │   ├── models/        # Data schemas
│   │   ├── services/      # Business logic services
│   │   └── utils/         # Utility functions
│   ├── tests/             # Unit and integration tests
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile         # Backend container image
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # API client services
│   │   └── types/         # TypeScript definitions
│   ├── package.json       # Node dependencies
│   ├── tsconfig.json      # TypeScript configuration
│   └── Dockerfile         # Frontend container image
├── sample_docs/           # Sample documentation
└── docker-compose.yml     # Multi-container configuration
```

## Testing

### Backend Tests

Run all tests:
```bash
cd backend
pytest
```

Run specific test file:
```bash
pytest tests/test_chunker.py -v
```

Run with coverage:
```bash
pytest --cov=app tests/
```

Available tests:
- `test_chunker.py` - Document chunking logic
- `test_guardrail.py` - Content safety validation
- `test_html_parser.py` - HTML parsing utilities
- `test_local_loader.py` - Local file loading
- `test_rag_pipeline.py` - RAG pipeline integration
- `test_routes.py` - API endpoint testing
- `test_semantic_cache.py` - Cache functionality
- `test_spell_check.py` - Spell checking utilities
- `test_vector_store.py` - Vector store operations

## Configuration

### Backend Configuration
Edit `backend/app/config.py` to customize:
- LLM model settings
- Embedding parameters
- Vector store configurations
- Cache settings
- Database connections

### Frontend Configuration
Edit `frontend/vite.config.ts` for:
- Development server settings
- Build optimization
- API proxy configuration

## Development

### Adding New API Routes

1. Create a new file in `backend/app/api/`
2. Define routes using FastAPI decorators
3. Add corresponding route in `backend/app/api/routes/`
4. Register routes in `backend/app/main.py`

### Adding New Components

1. Create component in `frontend/src/components/`
2. Define TypeScript interfaces in `frontend/src/types/`
3. Import and use in `App.tsx` or other components

## Performance Optimization

- **Semantic Caching**: Reduces redundant LLM calls for similar queries
- **Vector Indexing**: Fast similarity search using embeddings
- **Document Chunking**: Optimal chunk size for context windows
- **Lazy Loading**: Frontend components are lazy-loaded for better performance

## Security Considerations

- **Input Guardrails**: Validates all user inputs
- **Content Filtering**: Moderates generated responses
- **API Authentication**: Implement token-based auth for production
- **Secure Credentials**: Use environment variables for sensitive data
- **CORS Configuration**: Update for production domain

## Troubleshooting

### Backend Issues
- Check if port 8000 is available
- Verify environment variables are set correctly
- Ensure database file has write permissions
- Review logs in `backend/app/main.py` output

### Frontend Issues
- Clear browser cache and node_modules if experiencing issues
- Ensure API_BASE_URL points to correct backend
- Check browser console for errors

### Docker Issues
- Run `docker-compose down` and `docker-compose up --build` to rebuild
- Check logs with `docker-compose logs -f`
- Verify Docker daemon is running

## Contributing

1. Create a feature branch
2. Make your changes and add tests
3. Run tests to ensure nothing breaks
4. Submit a pull request with detailed description

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please open an issue in the repository.
