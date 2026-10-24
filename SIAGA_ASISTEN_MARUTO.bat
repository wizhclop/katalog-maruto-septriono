@echo off
title SISTEM SIAGA ASISTEN AI LOKAL - MARUTO ART STUDIO
color 0A
cls

cd /d "F:\DATABASE_AI ART\ART"

echo ================================================================
echo    MEMULAI ASISTEN TELEGRAM MULTI-PLATFORM HUB
echo ================================================================
echo.

python remote_asisten_telegram.py

echo.
echo ================================================================
echo [PERHATIAN] Skrip berhenti. Lihat pesan galat di atas!
echo ================================================================
pause
