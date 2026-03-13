@echo off
echo Starting AgroLink Frontend Server...
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo Error: Dependencies not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Start the development server
echo Starting React development server...
echo Frontend will be available at http://localhost:3000
echo.
npm start

pause