@echo off
title My Schedule Tool
color 0A

echo.
echo ================================================
echo       My Schedule Tool Launcher
echo ================================================
echo.



cd /d "C:\Users\EGShaaraOm\OneDrive - NESTLE\Attachments\Work\Software Solutions\Projects\My Schedule Tool"



echo Starting Streamlit application...

REM Try streamlit command first (suppress error output)
streamlit run src/main.py >nul 2>&1
if %errorlevel% neq 0 (
    REM If direct command fails, use Python module method
    python -m streamlit run src/main.py
)

pause