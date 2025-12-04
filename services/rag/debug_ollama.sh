#!/bin/bash

echo "Ollama Debugging"
echo "================"

echo -e "\n1. Check if Ollama is running:"
if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "✓ Ollama is running"
    curl -s http://localhost:11434/api/version | python3 -m json.tool
else
    echo "✗ Ollama is not running"
    echo "  Start with: ollama serve"
fi

echo -e "\n2. List installed models:"
curl -s http://localhost:11434/api/tags | python3 -m json.tool

echo -e "\n3. Test generation:"
curl -s http://localhost:11434/api/generate -d '{
  "model": "llama3.2:3b",
  "prompt": "Say hello in one sentence",
  "stream": false
}' | python3 -m json.tool