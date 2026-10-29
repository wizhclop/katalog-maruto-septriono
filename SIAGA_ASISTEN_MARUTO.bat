@echo off
title SISTEM SIAGA ASISTEN AI LOKAL - MARUTO ART STUDIO
color 0A
cls

echo ================================================================
echo    SISTEM SIAGA ASISTEN AI LOKAL - MARUTO ART DAN SKETCH
echo ================================================================
echo.

echo [1/3] Memeriksa Koneksi Internet...
ping -n 1 8.8.8.8 >nul 2>&1
if %errorlevel% neq 0 (
    echo [PERINGATAN] Internet belum terdeteksi.
) else (
    echo [OK] Koneksi Internet AKTIF.
)
echo.

echo [2/3] Menyegarkan sesi bot...
taskkill /F /IM python.exe /T >nul 2>&1
timeout /t 1 >nul
echo.

echo [3/3] Menjalankan Bot Terpadu...
echo ================================================================
echo STATUS SISTEM: SIAGA PENUH (STANDBY)
echo Jalur aktif: Katalog Lukisan ART dan Katalog Sketsa SKT
echo Tekan Ctrl + C jika ingin mematikan bot.
echo ================================================================
echo.

cd /d "F:\DATABASE_AI ART"
python bot_terpadu_maruto.py

echo.
pause
