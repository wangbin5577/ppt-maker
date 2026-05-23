@echo off
chcp 65001 >nul
title PPT Maker - Web UI
echo ========================================
echo   PPT Maker - Web UI
echo   浏览器打开: http://localhost:8503
echo   按 Ctrl+C 停止
echo ========================================
echo.
streamlit run "%~dp0app.py" --server.port 8503
pause
