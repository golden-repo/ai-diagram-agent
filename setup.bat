@echo off
echo 🚀 Starting AI Diagram System Setup for Windows...

:: 1. Create Virtual Environment
:: python -m venv venv
:: call venv\Scripts\activate

:: 2. Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install langgraph langchain_openai fastapi uvicorn playwright nest_asyncio python-multipart requests dotenv

:: 3. Install Playwright Browsers
echo 🌐 Installing Playwright Chromium browser...
playwright install chromium

:: 4. Create necessary folders
if not exist "logs" mkdir logs

echo ✅ Setup Complete! To start the server, run:
echo venv\Scripts\activate ^&^& uvicorn main:app --reload
pause