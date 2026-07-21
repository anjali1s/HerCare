#!/usr/bin/env bash
# One-command setup for Mac/Linux.
# Usage:  chmod +x setup.sh && ./setup.sh

set -e

echo "Checking Python version..."
python3 --version

echo "Creating virtual environment (.venv)..."
python3 -m venv .venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies (this can take a few minutes the first time)..."
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo ""
    echo ">>> IMPORTANT: open .env and paste your real Groq API key into it."
    echo ">>> Get a free key at: https://console.groq.com/keys"
else
    echo ".env already exists, leaving it as is."
fi

mkdir -p data

echo ""
echo "======================================================"
echo "Setup complete."
echo ""
echo "Next steps:"
echo "  1. Put your PDF/DOCX files into the 'data' folder."
echo "  2. Edit .env with your real GROQ_API_KEY (if not done yet)."
echo "  3. Run:  source .venv/bin/activate"
echo "  4. Run:  python ingestion_pipeline.py"
echo "  5. Run:  python rag_chatbot.py"
echo "======================================================"
