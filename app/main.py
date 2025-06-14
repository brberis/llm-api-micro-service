from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import asyncio
import logging
from typing import List, Optional, Dict, Any
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LLM Inference Service",
    description="A microservice for LLM inference using Ollama with Gemma2 model",
    version="1.0.0"
)

# Pydantic models
class InferenceRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    stream: Optional[bool] = False

class InferenceResponse(BaseModel):
    response: str
    model: str
    created_at: str
    done: bool
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None

class ModelInfo(BaseModel):
    name: str
    size: int
    digest: str
    details: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    message: str
    ollama_status: str
    available_models: List[str]

# Ollama client configuration
OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "gemma2:2b"

async def check_ollama_health() -> bool:
    """Check if Ollama service is running"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/version", timeout=5.0)
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Ollama health check failed: {e}")
        return False

async def get_available_models() -> List[str]:
    """Get list of available models from Ollama"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            return []
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        return []

async def ensure_model_loaded() -> bool:
    """Ensure the Gemma2 model is loaded and ready"""
    try:
        async with httpx.AsyncClient() as client:
            # Try a simple generation to warm up the model
            payload = {
                "model": MODEL_NAME,
                "prompt": "Hello",
                "stream": False,
                "options": {"num_predict": 1}
            }
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=30.0
            )
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Model loading check failed: {e}")
        return False

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "service": "LLM Inference Service",
        "version": "1.0.0",
        "model": MODEL_NAME,
        "status": "running"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    ollama_healthy = await check_ollama_health()
    available_models = await get_available_models()
    
    if ollama_healthy and MODEL_NAME in available_models:
        status = "healthy"
        message = "Service is running and model is available"
        ollama_status = "running"
    elif ollama_healthy:
        status = "partial"
        message = f"Ollama is running but {MODEL_NAME} is not available"
        ollama_status = "running"
    else:
        status = "unhealthy"
        message = "Ollama service is not responding"
        ollama_status = "not responding"
    
    return HealthResponse(
        status=status,
        message=message,
        ollama_status=ollama_status,
        available_models=available_models
    )

@app.post("/inference", response_model=InferenceResponse)
async def generate_inference(request: InferenceRequest):
    """Generate inference using the Gemma2 model"""
    
    # Check if Ollama is healthy
    if not await check_ollama_health():
        raise HTTPException(
            status_code=503,
            detail="Ollama service is not available"
        )
    
    try:
        # Prepare the request payload for Ollama
        payload = {
            "model": MODEL_NAME,
            "prompt": request.prompt,
            "stream": request.stream,
            "options": {
                "num_predict": request.max_tokens,
                "temperature": request.temperature,
                "top_p": request.top_p
            }
        }
        
        # Make request to Ollama
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=60.0
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama request failed: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Ollama request failed: {response.text}"
                )
            
            result = response.json()
            
            return InferenceResponse(
                response=result.get("response", ""),
                model=result.get("model", MODEL_NAME),
                created_at=result.get("created_at", ""),
                done=result.get("done", True),
                total_duration=result.get("total_duration"),
                load_duration=result.get("load_duration"),
                prompt_eval_count=result.get("prompt_eval_count"),
                prompt_eval_duration=result.get("prompt_eval_duration"),
                eval_count=result.get("eval_count"),
                eval_duration=result.get("eval_duration")
            )
            
    except httpx.TimeoutException:
        logger.error("Request to Ollama timed out")
        raise HTTPException(
            status_code=504,
            detail="Request timed out. The model might be loading or the prompt is too complex."
        )
    except Exception as e:
        logger.error(f"Inference request failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/models", response_model=List[str])
async def list_models():
    """List available models"""
    models = await get_available_models()
    return models

@app.get("/model/{model_name}", response_model=ModelInfo)
async def get_model_info(model_name: str):
    """Get information about a specific model"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/show",
                json={"name": model_name},
                timeout=10.0
            )
            
            if response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"Model '{model_name}' not found"
                )
            elif response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to get model information"
                )
            
            data = response.json()
            return ModelInfo(
                name=data.get("details", {}).get("name", model_name),
                size=data.get("size", 0),
                digest=data.get("digest", ""),
                details=data.get("details", {})
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.on_event("startup")
async def startup_event():
    """Startup event to ensure model is ready"""
    logger.info("Starting LLM Inference Service...")
    
    # Wait for Ollama to be ready
    max_retries = 30
    for i in range(max_retries):
        if await check_ollama_health():
            logger.info("Ollama service is ready")
            break
        logger.info(f"Waiting for Ollama service... ({i+1}/{max_retries})")
        await asyncio.sleep(2)
    else:
        logger.error("Ollama service did not become ready in time")
        return
    
    # Check if model is available
    models = await get_available_models()
    if MODEL_NAME in models:
        logger.info(f"Model {MODEL_NAME} is available")
        
        # Warm up the model
        logger.info("Warming up the model...")
        if await ensure_model_loaded():
            logger.info("Model is warmed up and ready")
        else:
            logger.warning("Model warm-up failed, but service will continue")
    else:
        logger.warning(f"Model {MODEL_NAME} is not available. Available models: {models}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)