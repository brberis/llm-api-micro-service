# Example Integration: Python Client

import requests
import asyncio
import aiohttp
from typing import Optional, Dict, Any

class MicroLLMService:
    """Client for interacting with Micro LLM Service"""
    
    def __init__(self, base_url: str = "http://localhost:8100"):
        self.base_url = base_url.rstrip('/')
    
    def generate_text(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate text using the LLM service
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            Dict containing the response and metadata
        """
        try:
            response = requests.post(
                f"{self.base_url}/inference",
                json={
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                },
                timeout=120
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def chat(self, message: str, max_tokens: int = 256, temperature: float = 0.8) -> Dict[str, Any]:
        """
        Send a chat message to the LLM service
        
        Args:
            message: The chat message
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Dict containing the response and metadata
        """
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json={
                    "prompt": message,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                },
                timeout=120
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Chat request failed: {str(e)}"}
    
    def is_healthy(self) -> bool:
        """Check if the service is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("status") == "healthy" and data.get("model_loaded", False)
            return False
        except:
            return False
    
    async def generate_text_async(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> Dict[str, Any]:
        """Async version of generate_text"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/inference",
                    json={
                        "prompt": prompt,
                        "max_tokens": max_tokens,
                        "temperature": temperature
                    },
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"HTTP {response.status}: {await response.text()}"}
        except Exception as e:
            return {"error": f"Async request failed: {str(e)}"}

# Example usage functions
def example_basic_usage():
    """Basic usage example"""
    print("🔍 Basic Usage Example")
    print("=" * 40)
    
    # Initialize client
    llm = MicroLLMService()
    
    # Check health
    if not llm.is_healthy():
        print("❌ Service is not healthy or not running")
        return
    
    # Generate text
    result = llm.generate_text("Explain machine learning in simple terms", max_tokens=200)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Generated text:\n{result['response']}")

def example_chat_conversation():
    """Chat conversation example"""
    print("\n🗣️ Chat Conversation Example")
    print("=" * 40)
    
    llm = MicroLLMService()
    
    if not llm.is_healthy():
        print("❌ Service is not healthy or not running")
        return
    
    # Simulate a conversation
    messages = [
        "Hello! Can you help me understand Docker?",
        "What are the main benefits of using containers?",
        "How do I create a Dockerfile?"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n{i}. User: {message}")
        result = llm.chat(message, max_tokens=150)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"Assistant: {result['response']}")

async def example_async_usage():
    """Async usage example"""
    print("\n⚡ Async Usage Example")
    print("=" * 40)
    
    llm = MicroLLMService()
    
    # Generate multiple responses concurrently
    prompts = [
        "What is Python?",
        "Explain REST APIs",
        "What is Docker?"
    ]
    
    tasks = [llm.generate_text_async(prompt, max_tokens=100) for prompt in prompts]
    results = await asyncio.gather(*tasks)
    
    for prompt, result in zip(prompts, results):
        print(f"\n📝 Prompt: {prompt}")
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Response: {result['response'][:100]}...")

def example_ai_assistant_integration():
    """Example of integrating LLM into an AI assistant"""
    print("\n🤖 AI Assistant Integration Example")
    print("=" * 40)
    
    class SimpleAIAssistant:
        def __init__(self):
            self.llm = MicroLLMService()
            self.conversation_history = []
        
        def process_query(self, user_input: str) -> str:
            """Process user query and return response"""
            if not self.llm.is_healthy():
                return "Sorry, the AI service is currently unavailable."
            
            # Add context from conversation history
            context = ""
            if self.conversation_history:
                context = "Previous conversation:\n"
                for entry in self.conversation_history[-3:]:  # Last 3 exchanges
                    context += f"User: {entry['user']}\nAssistant: {entry['assistant']}\n"
                context += "\nCurrent question:\n"
            
            full_prompt = context + user_input
            
            result = self.llm.generate_text(full_prompt, max_tokens=300, temperature=0.7)
            
            if "error" in result:
                return f"Sorry, I encountered an error: {result['error']}"
            
            response = result['response']
            
            # Store in conversation history
            self.conversation_history.append({
                "user": user_input,
                "assistant": response
            })
            
            return response
    
    # Demo the assistant
    assistant = SimpleAIAssistant()
    
    test_queries = [
        "What is artificial intelligence?",
        "How does it relate to machine learning?",
        "Can you give me a practical example?"
    ]
    
    for query in test_queries:
        print(f"\n👤 User: {query}")
        response = assistant.process_query(query)
        print(f"🤖 Assistant: {response}")

if __name__ == "__main__":
    # Run examples
    example_basic_usage()
    example_chat_conversation()
    
    # Run async example
    asyncio.run(example_async_usage())
    
    # AI assistant example
    example_ai_assistant_integration()
    
    print("\n" + "=" * 50)
    print("🎉 All examples completed!")
    print("\n💡 Tips for production use:")
    print("- Add proper error handling and retries")
    print("- Implement connection pooling for high throughput")
    print("- Add authentication and rate limiting")
    print("- Monitor response times and model performance")
    print("- Consider using async clients for better performance")
