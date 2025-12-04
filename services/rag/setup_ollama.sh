#!/bin/bash

echo "Setting up Ollama for RAG system"
echo "================================"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed"
    echo ""
    echo "Install Ollama:"
    echo "  Linux:   curl -fsSL https://ollama.com/install.sh | sh"
    echo "  Mac:     brew install ollama"
    echo "  Windows: Download from https://ollama.com/download"
    exit 1
fi

echo "✓ Ollama is installed"

# Start Ollama in background if not running
if ! curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "Starting Ollama service..."
    ollama serve > /dev/null 2>&1 &
    sleep 3
fi

# Check if running
if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "✓ Ollama is running"
else
    echo "❌ Failed to start Ollama"
    exit 1
fi

# Pull recommended model
echo ""
echo "Pulling llama3.2:3b model (this may take a few minutes)..."
ollama pull llama3.2:3b

echo ""
echo "✓ Setup complete!"
echo ""
echo "Available models:"
ollama list