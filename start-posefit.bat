@echo off
title PoseFit Startup Script
echo ======================================================
echo            PoseFit Application Starter
echo ======================================================
echo.

REM Set colors for better readability
color 0A

REM Check if required directories exist
if not exist "PoseFit_Trainer\AI_PersonTrainer backend" (
    color 0C
    echo ERROR: Backend directory not found!
    echo Please ensure the project structure is correct.
    goto :error
)

if not exist "PoseFit_Trainer\personal-trainer-auth" (
    color 0C
    echo ERROR: Frontend directory not found!
    echo Please ensure the project structure is correct.
    goto :error
)

if not exist "PoseFit_assistant" (
    color 0C
    echo ERROR: PoseFit Assistant directory not found!
    echo Please ensure the project structure is correct.
    goto :error
)

if not exist "posefit-landing" (
    color 0C
    echo ERROR: PoseFit Landing directory not found!
    echo Please ensure the project structure is correct.
    goto :error
)

REM Check for Python installation
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    color 0C
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python and ensure it's added to your PATH.
    goto :error
)

REM Check for Node.js installation
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    color 0C
    echo ERROR: Node.js is not installed or not in PATH!
    echo Please install Node.js and ensure it's added to your PATH.
    goto :error
)

REM Check .env file exists, if not generate it
if not exist "PoseFit_Trainer\AI_PersonTrainer backend\.env" (
    echo Creating .env file and generating secret key...
    cd "PoseFit_Trainer\AI_PersonTrainer backend"
    python generate_key.py
    cd ..\..
)

REM Check for Docker presence (optional)
where docker >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo Docker is available. Would you like to use Docker? (y/n)
    choice /c yn /n
    if %ERRORLEVEL% equ 1 (
        echo Starting with Docker...
        docker-compose up -d
        if %ERRORLEVEL% equ 0 (
            echo.
            echo ======================================================
            echo Application started successfully with Docker!
            echo The landing page is available at: http://localhost:4000
            echo The PoseFit Assistant is available at: http://localhost:3001
            echo The PoseFit Trainer is available at: http://localhost:3000
            echo The backend API is available at: http://localhost:8002
            echo API documentation: http://localhost:8002/api/docs
            echo ======================================================
            echo.
            echo Press any key to exit this window...
            pause >nul
            exit /b 0
        ) else (
            echo Docker failed to start. Falling back to direct execution...
        )
    )
)

REM Clean temp videos directory
echo Cleaning temporary video files...
if exist "PoseFit_Trainer\AI_PersonTrainer backend\temp_videos" (
    del /Q "PoseFit_Trainer\AI_PersonTrainer backend\temp_videos\*.*" >nul 2>&1
)

REM Check for and kill processes using port 8002
echo Checking for processes using port 8002...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8002"') do (
    echo Found process %%p using port 8002, terminating...
    taskkill /F /PID %%p >nul 2>&1
)

REM Kill any existing processes
echo Checking for existing processes...
taskkill /f /im python.exe /fi "WINDOWTITLE eq API Server" >nul 2>&1
taskkill /f /im node.exe /fi "WINDOWTITLE eq PoseFit Trainer" >nul 2>&1
taskkill /f /im node.exe /fi "WINDOWTITLE eq PoseFit Assistant" >nul 2>&1
taskkill /f /im node.exe /fi "WINDOWTITLE eq PoseFit Landing" >nul 2>&1
taskkill /f /im node.exe /fi "WINDOWTITLE eq Convex Dev Server" >nul 2>&1
taskkill /f /im uvicorn* >nul 2>&1

REM First, start the API server
echo Starting backend API server...
start "API Server" cmd /k "cd PoseFit_Trainer\AI_PersonTrainer backend && python api_server.py"

REM Wait a moment to ensure API server starts first
echo Waiting for API server to initialize...
timeout /t 5 /nobreak >nul

REM Check if port 8002 is in use
netstat -ano | find ":8002" >nul
if %ERRORLEVEL% equ 0 (
    echo API server appears to be running on port 8002.
) else (
    echo WARNING: API server may not have started correctly.
    echo Please check the API Server window for errors.
    pause
)

REM Start the PoseFit Trainer frontend
echo Starting PoseFit Trainer frontend...
start "PoseFit Trainer" cmd /k "cd PoseFit_Trainer\personal-trainer-auth && set PORT=3000 && npm run dev"

REM Start the Convex development server for PoseFit Assistant
echo Starting Convex development server...
start "Convex Dev Server" cmd /k "cd PoseFit_assistant && npx convex dev"

REM Start the PoseFit Assistant
echo Starting PoseFit Assistant...
start "PoseFit Assistant" cmd /k "cd PoseFit_assistant && set PORT=3001 && npm run dev"

REM Start the Landing Page
echo Starting PoseFit Landing Page...
start "PoseFit Landing" cmd /k "cd posefit-landing && set PORT=4000 && npm run dev"

echo.
echo ======================================================
echo All services are starting. Please wait a moment for them to initialize.
echo.
echo The landing page is available at: http://localhost:4000
echo The PoseFit Assistant is available at: http://localhost:3001
echo The PoseFit Trainer is available at: http://localhost:3000
echo The backend API is available at: http://localhost:8002
echo API documentation: http://localhost:8002/api/docs
echo.
echo If you have connection issues:
echo  1. Ensure Python is installed with all required packages
echo  2. Ensure Node.js is installed
echo  3. Check that required ports are free (8002, 3000, 3001, 4000)
echo ======================================================
echo.
goto :end

:error
echo.
echo Failed to start services. Please fix the issues and try again.
pause
exit /b 1

:end
echo Services started successfully! 
echo Press any key to exit this window...
pause >nul 