@echo off
echo Setting up AgroLink Complete Environment...
echo.

echo Setting up Backend...
cd agrolink-backend
call setup.bat
cd ..

echo Setting up Frontend...
cd agrolink-frontend
call setup.bat
cd ..

echo.
echo Setup completed for both frontend and backend!
echo.
echo To run the complete application:
echo 1. In one terminal, run the backend: cd agrolink-backend ^&^& run.bat
echo 2. In another terminal, run the frontend: cd agrolink-frontend ^&^& run.bat
echo.
pause