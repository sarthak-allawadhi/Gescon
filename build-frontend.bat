@echo off
echo ====================================================
echo  Gescon Vercel Export Automation Script
echo ====================================================
echo.
echo [1/2] Activating Python virtual environment and compiling frontend...
call venv\Scripts\activate.bat
python -m reflex export --frontend-only
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Reflex export failed! Make sure your venv is set up correctly.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/2] Frontend compiled successfully!
echo Output zip file: frontend.zip
echo Output directory: .web\build\client\
echo.
echo To deploy to Vercel, run:
echo    vercel deploy --prod .web\build\client
echo.
echo Press any key to exit...
pause
