#!/bin/bash
echo "🚀 Starting AI Diagram System Setup for Mac/Linux..."

# 1. Create Virtual Environment
python3 -m venv venv
source venv/bin/activate

# 2. Upgrade pip and install dependencies
pip install --upgrade pip
pip install langgraph langchain_openai fastapi uvicorn playwright nest_asyncio python-multipart requests dotenv

# 3. Install Playwright Browsers
echo "🌐 Installing Playwright Chromium browser..."
playwright install chromium

# 4. Create necessary folders
mkdir -p logs

echo "✅ Setup Complete! To start the server, run:"
echo "source venv/bin/activate && uvicorn main:app --reload"