@echo off
title SVN Log Kontrol Araci
color 0A

echo SVN Kontrol Baslatiliyor...
python svn_checker.py

echo.
echo ==========================================
echo Raporlama islemi bitti. Cikmak icin bir tusa basin...

REM --- MAIL GONDERME KODU  ---
powershell -ExecutionPolicy Bypass -Command ^
	"$outlook = New-Object -ComObject Outlook.Application;" ^
	"$mail = $outlook.CreateItem(0);" ^
	"$mail.To = '---------------';" ^
	"$mail.Subject = 'Günlük İşlem Tamamlandı';" ^
	"$mail.Body = 'Merhaba, \n\nHer sabah saat 8:00''da planlanan batch dosyası basariyla calistirildi.\n\nSaygilar.';" ^
	"$mail.Send();"

echo Mail gonderildi.

pause
	