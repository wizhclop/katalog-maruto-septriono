@echo off
title Server Web Portofolio Art Maruto Septriono
echo ========================================================
echo   Menjalankan Server Lokal Portofolio Maruto Septriono  
echo   Port: 8000 ^| Folder: F:\DATABASE_AI ART\ART
echo ========================================================
echo.
echo Membuka katalog di browser...
start http://localhost:8000/index.html

echo Menyalakan server lokal... (Jangan tutup jendela ini saat membuka web)
cd /d "F:\DATABASE_AI ART\ART"
python -m http.server 8000
pause
