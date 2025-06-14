#!/bin/bash

# Start Ollama in the background
ollama serve &

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
sleep 10

# Check if Ollama is responding
while ! curl -s http://localhost:11434/api/version > /dev/null; do
    echo "Waiting for Ollama to be ready..."
    sleep 2
done

echo "Ollama is ready!"

# Pull the Gemma2:2b model if not already present
echo "Checking for Gemma2:2b model..."
if ! ollama list | grep -q "gemma2:2b"; then
    echo "Pulling Gemma2:2b model (this may take a few minutes)..."
    ollama pull gemma2:2b
else
    echo "Gemma2:2b model already available"
fi

# Start the FastAPI service
echo "Starting FastAPI service..."
python main.py