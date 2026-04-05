@echo off
TITLE G CLI - Multi-Brain AI OS Setup
COLOR 0B

echo ==============================================
echo    G CLI - Multi-Brain AI OS Setup (Windows)  
echo ==============================================
echo.

:: Check for Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    COLOR 0C
    echo [X] Error: Python 3 is not installed or not in your PATH.
    echo Please install Python 3.10+ from https://www.python.org/downloads/windows/
    echo IMPORTANT: Make sure to check the box "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [*] Python 3 detected. Proceeding with installation...

:: Get project root (two levels up from Landing_Page\Windows)
pushd "%~dp0\..\.."

echo [*] Installing dependencies and building G CLI...
python -m pip install . --user

popd

echo.
echo ==============================================
echo [SUCCESS] G CLI has been successfully installed!
echo.
echo Close this Command Prompt and open a new one.
echo Then type:
echo    g
echo.
echo If 'g' is not recognized, you may need to add Python Scripts to your PATH.
echo ==============================================
pause
