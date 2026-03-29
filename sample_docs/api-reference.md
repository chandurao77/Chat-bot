# API Reference

## Authentication
All API calls require header: `X-API-Key: your-key`

## Endpoints

### GET /api/health
Returns system health status.

### POST /api/chat/stream
Send a question and receive streaming response.
Request body: { "question": "your question here" }

### POST /api/ingest
Trigger document ingestion. Requires API key.

### GET /api/conversations
List all conversations.

## Error Codes
- 401: Invalid API key
- 429: Rate limit exceeded (30 req/min)
- 500: Internal server error
