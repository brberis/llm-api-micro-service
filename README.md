# Micro LLM Service

A lightweight Docker-based LLM inference microservice using Gemma2 (2B model) for CPU-only deployments.

## Features

- **CPU-Only**: Optimized for CPU inference using Gemma2:2b model (~2GB storage)
- **FastAPI**: RESTful API with automatic documentation
- **Docker Compose**: Easy deployment and management
- **Health Checks**: Built-in monitoring and status endpoints
- **Multiple Endpoints**: Support for both single inference and chat-style conversations

## Quick Start

1. **Build and start the service:**
   ```bash
   docker-compose up --build
   ```

2. **Wait for model download** (first run only):
   The service will automatically download the Gemma2:2b model (~2GB) on first startup.

3. **Test the service:**
   ```bash
   curl http://localhost:8100/health
   ```

## API Endpoints

### Base URL: `http://localhost:8100`

- **GET /** - API information and usage
- **GET /health** - Health check and model status
- **GET /models** - List available models
- **POST /inference** - Single inference request
- **POST /chat** - Chat-style conversation
- **POST /load-model** - Manually load a model
- **GET /docs** - Interactive API documentation (Swagger UI)

## Usage Examples

### Simple Inference
```bash
curl -X POST "http://localhost:8100/inference" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "Explain quantum computing in simple terms",
       "max_tokens": 512,
       "temperature": 0.7
     }'
```

### Chat Conversation
```bash
curl -X POST "http://localhost:8100/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "Hello, how are you?",
       "max_tokens": 256,
       "temperature": 0.8
     }'
```

### Health Check
```bash
curl http://localhost:8100/health
```

## Request Format

```json
{
  "prompt": "Your question or prompt here",
  "max_tokens": 512,
  "temperature": 0.7,
  "stream": false
}
```

## Response Format

```json
{
  "response": "Generated response text",
  "model": "gemma2:2b",
  "created_at": "2025-06-13T...",
  "done": true
}
```

## Integration with Other Services

This microservice is designed to be consumed by other software components. Here's how to integrate:

### Python Client Example
```python
import requests

def call_llm_service(prompt: str, max_tokens: int = 512):
    response = requests.post(
        "http://localhost:8100/inference",
        json={
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
    )
    return response.json()["response"]

# Usage
result = call_llm_service("What is machine learning?")
print(result)
```

### JavaScript/Node.js Client Example
```javascript
async function callLLMService(prompt, maxTokens = 512) {
    const response = await fetch('http://localhost:8100/inference', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            prompt: prompt,
            max_tokens: maxTokens,
            temperature: 0.7
        })
    });
    const data = await response.json();
    return data.response;
}

// Usage
const result = await callLLMService("Explain neural networks");
console.log(result);
```

## Configuration

### Environment Variables
- `OLLAMA_HOST=0.0.0.0` - Ollama server host
- `OLLAMA_ORIGINS=*` - Allowed CORS origins

### Model Configuration
The service uses Gemma2:2b by default for optimal CPU performance. To use a different model:

1. Edit `app/main.py` and change `MODEL_NAME`
2. Rebuild the container: `docker-compose up --build`

Available Gemma2 variants:
- `gemma2:2b` - ~2GB (recommended for CPU)
- `gemma2:9b` - ~5GB (requires more RAM)
- `gemma2:27b` - ~15GB (high-end servers only)

## Performance Notes

- **CPU Inference**: Optimized for CPU-only environments
- **Memory Usage**: ~4-6GB RAM recommended for smooth operation
- **Storage**: ~2GB for model storage
- **Response Time**: 5-30 seconds depending on prompt complexity and hardware

## Troubleshooting

### Service Not Starting
```bash
# Check logs
docker-compose logs micro-llm

# Check if ports are available
netstat -tulpn | grep -E '8000|11434'
```

### Model Download Issues
```bash
# Manually pull the model
docker-compose exec micro-llm ollama pull gemma2:2b
```

### API Not Responding
```bash
# Check health endpoint
curl -v http://localhost:8100/health

# Check Ollama status
curl http://localhost:11434/api/version
```

## Development

### Local Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Start Ollama separately
ollama serve

# Run the FastAPI app
cd app && python main.py
```

### Testing
```bash
# Run health check
curl http://localhost:8100/health

# Test inference
curl -X POST http://localhost:8100/inference \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello world!"}'
```

## Production Deployment

For production use:

1. **Use reverse proxy** (nginx/traefik) for SSL termination
2. **Set resource limits** in docker-compose.yml
3. **Configure logging** and monitoring
4. **Use persistent volumes** for model storage
5. **Implement authentication** if needed

## License

This project is open source. See LICENSE file for details.
