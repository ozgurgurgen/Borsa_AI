@echo off
chcp 65001 >nul
title Masaustu Kisayolu Olusturucu
color 0B

echo.
echo 🔗 AI-FTB MASAUSTU KISA YOLLAR
echo ===============================
echo.

cd /d "C:\Users\gurge\Desktop\BorsAI"

echo 📋 Masaustu kisayollari olusturuluyor...

REM Ana kontrol paneli kısayolu
echo Set WshShell = WScript.CreateObject("WScript.Shell") > temp_shortcut.vbs
echo Set Shortcut = WshShell.CreateShortcut("C:\Users\gurge\Desktop\🤖 AI-FTB Kontrol Paneli.lnk") >> temp_shortcut.vbs
echo Shortcut.TargetPath = "C:\Users\gurge\Desktop\BorsAI\master_control.bat" >> temp_shortcut.vbs
echo Shortcut.WorkingDirectory = "C:\Users\gurge\Desktop\BorsAI" >> temp_shortcut.vbs
echo Shortcut.Description = "AI-FTB Proje Yönetim Merkezi" >> temp_shortcut.vbs
echo Shortcut.Save >> temp_shortcut.vbs
cscript temp_shortcut.vbs >nul

REM Hızlı başlatma kısayolu
echo Set WshShell = WScript.CreateObject("WScript.Shell") > temp_shortcut2.vbs
echo Set Shortcut = WshShell.CreateShortcut("C:\Users\gurge\Desktop\🚀 AI-FTB Hızlı Başlat.lnk") >> temp_shortcut2.vbs
echo Shortcut.TargetPath = "C:\Users\gurge\Desktop\BorsAI\quick_start.bat" >> temp_shortcut2.vbs
echo Shortcut.WorkingDirectory = "C:\Users\gurge\Desktop\BorsAI" >> temp_shortcut2.vbs
echo Shortcut.Description = "AI-FTB Projesi Hızlı Başlatma" >> temp_shortcut2.vbs
echo Shortcut.Save >> temp_shortcut2.vbs
cscript temp_shortcut2.vbs >nul

REM GitHub yukleme kisayolu
echo Set WshShell = WScript.CreateObject("WScript.Shell") > temp_shortcut3.vbs
echo Set Shortcut = WshShell.CreateShortcut("C:\Users\gurge\Desktop\📤 GitHub'a Yukle.lnk") >> temp_shortcut3.vbs
echo Shortcut.TargetPath = "C:\Users\gurge\Desktop\BorsAI\upload_to_github.bat" >> temp_shortcut3.vbs
echo Shortcut.WorkingDirectory = "C:\Users\gurge\Desktop\BorsAI" >> temp_shortcut3.vbs
echo Shortcut.Description = "AI-FTB Projesini GitHub'a Yukle" >> temp_shortcut3.vbs
echo Shortcut.Save >> temp_shortcut3.vbs
cscript temp_shortcut3.vbs >nul

REM Gecici dosyalari temizle
del temp_shortcut.vbs temp_shortcut2.vbs temp_shortcut3.vbs

echo ✅ Masaustu kisayollari olusturuldu!
echo.
echo 🔗 Olusturulan kisayollar:
echo   🤖 AI-FTB Kontrol Paneli - Ana menu
echo   🚀 AI-FTB Hizli Baslat - Tek tikla baslat
echo   📤 GitHub'a Yukle - Proje yukleme
echo.
echo 💡 Artik masaustunden tek tikla erisebilirsiniz!
echo.
pause
