@echo off
chcp 65001 >nul
title SVN Log Kontrol Araci
color 0A

echo ==========================================
echo       SVN Log Kontrol Aracı Başlatılıyor
echo ==========================================
echo.

REM --- 1. PYTHON KODUNU ÇALIŞTIR ---
python svn_checker.py

REM --- 2. HATA KONTROLÜ ---
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo.
    echo [HATA] Python betiğinde hata oluştu! (Kod: %ERRORLEVEL%)
    echo Rapor oluşturulamadığı için mail gönderilmedi.
    echo.
    goto :SON
)

echo.
echo [BİLGİ] SVN kontrolleri tamamlandı.
echo [BİLGİ] Log klasörü sıkıştırılıyor ve mail hazırlanıyor...

REM --- 3. LOG KLASÖRÜNÜ BUL, ZIPLE VE MAİL AT ---
powershell -ExecutionPolicy Bypass -Command ^
    "$baseDir = '%~dp0'.TrimEnd('\');" ^
    "$configPath = Join-Path $baseDir 'config.json';" ^
    "$targetDir = $baseDir;" ^
    "if (Test-Path $configPath) {" ^
    "    $cfg = Get-Content $configPath -Raw | ConvertFrom-Json;" ^
    "    if ($cfg.output_dir -and (Test-Path $cfg.output_dir)) { $targetDir = $cfg.output_dir }" ^
    "};" ^
    "$latestFolder = Get-ChildItem -Path $targetDir -Directory -Filter 'log-*' | Sort-Object CreationTime -Descending | Select-Object -First 1;" ^
    "if ($latestFolder) {" ^
    "    $zipPath = Join-Path $targetDir ($latestFolder.Name + '.zip');" ^
    "    Compress-Archive -Path $latestFolder.FullName -DestinationPath $zipPath -Force;" ^
    "    $outlook = New-Object -ComObject Outlook.Application;" ^
    "    $mail = $outlook.CreateItem(0);" ^
    "    $mail.To = '---------------';" ^
    "    $mail.Subject = 'Günlük SVN Log Raporu - ' + $latestFolder.Name;" ^
    "    $mail.HTMLBody = '<p>Merhaba,</p><p>Günlük SVN log kontrol işlemi tamamlanmıştır.</p><p><b>Oluşturulan Klasör:</b> ' + $latestFolder.FullName + '</p><p>İlgili log ve diff raporları ekteki zip dosyasında yer almaktadır.</p><p>İyi çalışmalar.</p>';" ^
    "    $mail.Attachments.Add($zipPath);" ^
    "    $mail.Send();" ^
    "    Start-Sleep -Seconds 1;" ^
    "    Remove-Item -Path $zipPath -Force;" ^
    "    Write-Host '[BAŞARILI] ' $latestFolder.Name ' klasörü maile eklendi ve geçici zip temizlendi.';" ^
    "} else {" ^
    "    Write-Host '[UYARI] Gönderilecek log-* klasörü bulunamadı! ($targetDir dizinine bakıldı)';" ^
    "}"

:SON
echo.
echo ==========================================
echo İşlem bitti. Çıkmak için bir tuşa basın...
echo ==========================================
pause >nul