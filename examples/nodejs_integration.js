// Example Integration: Node.js/JavaScript Client

const axios = require('axios');

class MicroLLMService {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.client = axios.create({
            baseURL: this.baseUrl,
            timeout: 120000, // 2 minutes
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }

    /**
     * Generate text using the LLM service
     * @param {string} prompt - The input prompt
     * @param {number} maxTokens - Maximum tokens to generate
     * @param {number} temperature - Sampling temperature (0.0 to 1.0)
     * @returns {Promise<object>} Response object
     */
    async generateText(prompt, maxTokens = 512, temperature = 0.7) {
        try {
            const response = await this.client.post('/inference', {
                prompt,
                max_tokens: maxTokens,
                temperature
            });
            return response.data;
        } catch (error) {
            return { error: `Request failed: ${error.message}` };
        }
    }

    /**
     * Send a chat message to the LLM service
     * @param {string} message - The chat message
     * @param {number} maxTokens - Maximum tokens to generate
     * @param {number} temperature - Sampling temperature
     * @returns {Promise<object>} Response object
     */
    async chat(message, maxTokens = 256, temperature = 0.8) {
        try {
            const response = await this.client.post('/chat', {
                prompt: message,
                max_tokens: maxTokens,
                temperature
            });
            return response.data;
        } catch (error) {
            return { error: `Chat request failed: ${error.message}` };
        }
    }

    /**
     * Check if the service is healthy
     * @returns {Promise<boolean>} Health status
     */
    async isHealthy() {
        try {
            const response = await this.client.get('/health');
            const data = response.data;
            return data.status === 'healthy' && data.model_loaded;
        } catch {
            return false;
        }
    }

    /**
     * Get list of available models
     * @returns {Promise<object>} Models list
     */
    async getModels() {
        try {
            const response = await this.client.get('/models');
            return response.data;
        } catch (error) {
            return { error: `Failed to get models: ${error.message}` };
        }
    }
}

// Example usage functions
async function basicUsageExample() {
    console.log('🔍 Basic Usage Example');
    console.log('='.repeat(40));

    const llm = new MicroLLMService();

    // Check health
    const isHealthy = await llm.isHealthy();
    if (!isHealthy) {
        console.log('❌ Service is not healthy or not running');
        return;
    }

    // Generate text
    const result = await llm.generateText(
        'Explain web development in simple terms',
        200
    );

    if (result.error) {
        console.log(`❌ Error: ${result.error}`);
    } else {
        console.log(`✅ Generated text:\n${result.response}`);
    }
}

async function chatConversationExample() {
    console.log('\n🗣️ Chat Conversation Example');
    console.log('='.repeat(40));

    const llm = new MicroLLMService();

    if (!(await llm.isHealthy())) {
        console.log('❌ Service is not healthy or not running');
        return;
    }

    const messages = [
        'Hello! Can you help me with JavaScript?',
        'What are the main features of ES6?',
        'How do I use async/await?'
    ];

    for (let i = 0; i < messages.length; i++) {
        const message = messages[i];
        console.log(`\n${i + 1}. User: ${message}`);
        
        const result = await llm.chat(message, 150);
        
        if (result.error) {
            console.log(`❌ Error: ${result.error}`);
        } else {
            console.log(`Assistant: ${result.response}`);
        }
    }
}

async function batchProcessingExample() {
    console.log('\n⚡ Batch Processing Example');
    console.log('='.repeat(40));

    const llm = new MicroLLMService();

    const prompts = [
        'What is React?',
        'Explain Node.js',
        'What is MongoDB?'
    ];

    // Process all prompts concurrently
    const promises = prompts.map(prompt => 
        llm.generateText(prompt, 100)
    );

    const results = await Promise.all(promises);

    prompts.forEach((prompt, index) => {
        console.log(`\n📝 Prompt: ${prompt}`);
        const result = results[index];
        if (result.error) {
            console.log(`❌ Error: ${result.error}`);
        } else {
            console.log(`✅ Response: ${result.response.substring(0, 100)}...`);
        }
    });
}

class WebChatbot {
    constructor() {
        this.llm = new MicroLLMService();
        this.conversationHistory = [];
    }

    async processMessage(userMessage) {
        if (!(await this.llm.isHealthy())) {
            return 'Sorry, the AI service is currently unavailable.';
        }

        // Build context from conversation history
        let context = '';
        if (this.conversationHistory.length > 0) {
            context = 'Previous conversation:\n';
            const recentHistory = this.conversationHistory.slice(-3); // Last 3 exchanges
            recentHistory.forEach(entry => {
                context += `User: ${entry.user}\nAssistant: ${entry.assistant}\n`;
            });
            context += '\nCurrent question:\n';
        }

        const fullPrompt = context + userMessage;
        const result = await this.llm.generateText(fullPrompt, 300, 0.7);

        if (result.error) {
            return `Sorry, I encountered an error: ${result.error}`;
        }

        const response = result.response;

        // Store in conversation history
        this.conversationHistory.push({
            user: userMessage,
            assistant: response
        });

        // Keep only last 10 exchanges to prevent context from growing too large
        if (this.conversationHistory.length > 10) {
            this.conversationHistory = this.conversationHistory.slice(-10);
        }

        return response;
    }

    clearHistory() {
        this.conversationHistory = [];
    }
}

async function chatbotExample() {
    console.log('\n🤖 Web Chatbot Example');
    console.log('='.repeat(40));

    const chatbot = new WebChatbot();

    const testQueries = [
        'Hello, I need help with web development',
        'What frontend frameworks do you recommend?',
        'How do I choose between React and Vue?',
        'What about backend technologies?'
    ];

    for (const query of testQueries) {
        console.log(`\n👤 User: ${query}`);
        const response = await chatbot.processMessage(query);
        console.log(`🤖 Chatbot: ${response}`);
    }
}

// Express.js integration example
function expressIntegrationExample() {
    console.log('\n🌐 Express.js Integration Example');
    console.log('='.repeat(40));

    const expressCode = `
// Express.js server with LLM integration
const express = require('express');
const { MicroLLMService } = require('./micro-llm-client');

const app = express();
const llm = new MicroLLMService();

app.use(express.json());

// Health check endpoint
app.get('/health', async (req, res) => {
    const isHealthy = await llm.isHealthy();
    res.json({ healthy: isHealthy });
});

// Chat endpoint
app.post('/api/chat', async (req, res) => {
    try {
        const { message, maxTokens = 256 } = req.body;
        
        if (!message) {
            return res.status(400).json({ error: 'Message is required' });
        }

        const result = await llm.chat(message, maxTokens);
        
        if (result.error) {
            return res.status(500).json({ error: result.error });
        }

        res.json({ 
            response: result.response,
            model: result.model 
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Generate text endpoint
app.post('/api/generate', async (req, res) => {
    try {
        const { prompt, maxTokens = 512, temperature = 0.7 } = req.body;
        
        if (!prompt) {
            return res.status(400).json({ error: 'Prompt is required' });
        }

        const result = await llm.generateText(prompt, maxTokens, temperature);
        
        if (result.error) {
            return res.status(500).json({ error: result.error });
        }

        res.json({
            text: result.response,
            model: result.model
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(3000, () => {
    console.log('Server running on port 3000');
});
`;

    console.log(expressCode);
}

// Main execution
async function main() {
    try {
        await basicUsageExample();
        await chatConversationExample();
        await batchProcessingExample();
        await chatbotExample();
        expressIntegrationExample();

        console.log('\n' + '='.repeat(50));
        console.log('🎉 All examples completed!');
        console.log('\n💡 Tips for production use:');
        console.log('- Add proper error handling and retries');
        console.log('- Implement connection pooling for high throughput');
        console.log('- Add authentication and rate limiting');
        console.log('- Monitor response times and model performance');
        console.log('- Use PM2 or similar for process management');
        console.log('- Consider implementing caching for common queries');
    } catch (error) {
        console.error('Error running examples:', error);
    }
}

// Package.json example
const packageJsonExample = {
    "name": "micro-llm-client",
    "version": "1.0.0",
    "description": "Node.js client for Micro LLM Service",
    "main": "index.js",
    "dependencies": {
        "axios": "^1.6.0",
        "express": "^4.18.0"
    },
    "scripts": {
        "start": "node index.js",
        "test": "node examples.js"
    }
};

console.log('📦 Package.json for Node.js integration:');
console.log(JSON.stringify(packageJsonExample, null, 2));

// Run examples if this file is executed directly
if (require.main === module) {
    main();
}

module.exports = { MicroLLMService, WebChatbot };
