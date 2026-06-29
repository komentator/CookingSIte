@echo off
setlocal enabledelayedexpansion

echo ========================================
echo 🍳 CookingSite - Quick Start
echo ========================================

REM Check if .env exists
if not exist backend\.env (
  echo Creating backend\.env from .env.example
  copy .env.example backend\.env
  echo WARNING: Please edit backend\.env and add OPENAI_API_KEY
)

REM Setup Backend
echo.
echo === Setting up Backend ===
cd backend

if not exist venv (
  echo Creating virtual environment...
  python -m venv venv
)

echo Activating venv and installing dependencies...
call venv\Scripts\activate.bat
pip install -q -r requirements.txt

cd ..

REM Setup Frontend
echo.
echo === Setting up Frontend ===
cd frontend
call npm install --quiet
cd ..

REM Start PostgreSQL (if Docker available)
echo.
echo === Checking PostgreSQL ===
docker ps | findstr cookingsite-db >nul 2>&1
if errorlevel 1 (
  echo Starting PostgreSQL container...
  docker run -d ^
    --name cookingsite-db ^
    -e POSTGRES_USER=cookingsite ^
    -e POSTGRES_PASSWORD=password ^
    -e POSTGRES_DB=cookingsite ^
    -p 5432:5432 ^
    postgres:16-alpine >nul 2>&1
  echo PostgreSQL started
) else (
  echo PostgreSQL already running
)

timeout /t 3 /nobreak >nul

REM Start components
echo.
echo === Starting Components ===
echo.
echo Frontend running on http://localhost:3000
echo Backend running on http://localhost:8000
echo API Docs at http://localhost:8000/docs
echo.

REM Start Backend in new window
cd backend
start "CookingSite Backend" cmd /k "venv\Scripts\activate.bat && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
cd ..

REM Start Frontend in new window
cd frontend
start "CookingSite Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ✅ Services started in separate windows!
echo Press Ctrl+C in each window to stop

pause
