@echo off
REM One-command setup for Windows.
REM Usage: double-click setup.bat, or run it from cmd/PowerShell.

echo Checking Python version...
python --version

echo Creating virtual environment (.venv)...
python -m venv .venv

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing dependencies (this can take a few minutes the first time)...
python -m pip install --upgrade pip
pip install -r requirements.txt

if not exist .env (
    echo Creating .env from template...
    copy .env.example .env
    echo.
    echo ^>^>^> IMPORTANT: open .env and paste your real Groq API key into it.
    echo ^>^>^> Get a free key at: https://console.groq.com/keys
) else (
    echo .env already exists, leaving it as is.
)

if not exist data mkdir data

echo.
echo ======================================================
echo Setup complete.
echo.
echo Next steps:
echo   1. Put your PDF/DOCX files into the 'data' folder.
echo   2. Edit .env with your real GROQ_API_KEY (if not done yet).
echo   3. Run:  .venv\Scripts\activate.bat
echo   4. Run:  python ingestion_pipeline.py
echo   5. Run:  python rag_chatbot.py
echo ======================================================
pause
