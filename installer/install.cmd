@echo off
chcp 65001 >nul 2>&1
title mkusha iOS Installer

echo.
echo ========================================
echo   mkusha iOS Installer
echo   Auto-download and install to iPhone
echo ========================================
echo.

:: Check Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python not found!
    echo Download Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

:: Run installer
python "%~dp0install.py"

pause
