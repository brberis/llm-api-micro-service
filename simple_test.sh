#!/bin/bash

echo "=== Testing LLM Inference Service ==="
echo

echo "1. Testing root endpoint:"
curl -s http://localhost:8000/ | python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), indent=2))"
echo

echo "2. Testing health endpoint:"
curl -s http://localhost:8000/health | python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), indent=2))"
echo

echo "3. Testing models endpoint:"
curl -s http://localhost:8000/models
echo
echo

echo "4. Testing inference endpoint:"
echo "Request: What is 2+2?"
response=$(curl -s -X POST http://localhost:8000/inference \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is 2+2? Answer briefly.", "max_tokens": 20}')

echo "Response:"
echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print('Response:', data['response']); print('Model:', data['model']); print('Done:', data['done'])"
echo

echo "=== All tests completed ==="
