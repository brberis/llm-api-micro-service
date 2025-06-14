# Micro LLM Test Client

import requests
import json
import time

class MicroLLMClient:
    def __init__(self, base_url="http://localhost:8100"):
        self.base_url = base_url
    
    def health_check(self):
        """Check if the service is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def inference(self, prompt, max_tokens=512, temperature=0.7):
        """Send a single inference request"""
        try:
            payload = {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            response = requests.post(f"{self.base_url}/inference", json=payload)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def chat(self, message, max_tokens=256, temperature=0.8):
        """Send a chat-style message"""
        try:
            payload = {
                "prompt": message,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            response = requests.post(f"{self.base_url}/chat", json=payload)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def list_models(self):
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/models")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def main():
    """Test the LLM service"""
    client = MicroLLMClient()
    
    print("🔍 Testing Micro LLM Service...")
    print("=" * 50)
    
    # Health check
    print("\n1. Health Check:")
    health = client.health_check()
    print(json.dumps(health, indent=2))
    
    if health.get("status") != "healthy":
        print("❌ Service is not healthy. Please check the service.")
        return
    
    # List models
    print("\n2. Available Models:")
    models = client.list_models()
    print(json.dumps(models, indent=2))
    
    # Test inference
    print("\n3. Testing Inference:")
    test_prompts = [
        "What is artificial intelligence?",
        "Explain the benefits of renewable energy.",
        "Write a short poem about programming."
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n3.{i} Prompt: {prompt}")
        print("-" * 30)
        
        start_time = time.time()
        result = client.inference(prompt, max_tokens=256)
        end_time = time.time()
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Response ({end_time - start_time:.2f}s):")
            print(result.get("response", "No response"))
    
    # Test chat
    print("\n4. Testing Chat:")
    chat_messages = [
        "Hello! How are you?",
        "Can you help me with coding?",
        "Thank you!"
    ]
    
    for i, message in enumerate(chat_messages, 1):
        print(f"\n4.{i} Chat: {message}")
        print("-" * 30)
        
        start_time = time.time()
        result = client.chat(message, max_tokens=128)
        end_time = time.time()
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Response ({end_time - start_time:.2f}s):")
            print(result.get("response", "No response"))
    
    print("\n" + "=" * 50)
    print("🎉 Testing completed!")

if __name__ == "__main__":
    main()
