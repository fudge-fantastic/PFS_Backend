@echo off
echo 🚀 Starting PixelForge Backend Development Setup...
echo ============================================================

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Copy environment file if it doesn't exist
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please update .env with your configuration!
)

REM Initialize database (optional)
set /p init_db="Do you want to initialize the database with sample data? (y/n): "
if /i "%init_db%"=="y" (
    echo Initializing database...
    python scripts\init_db.py
)

REM Start the development server
set /p start_server="Do you want to start the development server? (y/n): "
if /i "%start_server%"=="y" (
    echo Starting development server...
    echo API will be available at: http://localhost:8000
    echo Swagger UI: http://localhost:8000/docs
    echo ReDoc: http://localhost:8000/redoc
    python run.py
) else (
    echo Setup completed! To start the server manually, run: python run.py
)

pause
