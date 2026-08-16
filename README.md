# SVN Log & Revizyon Kontrol Aracı

Bu uygulama, belirlenen SVN projelerindeki (lokal ve sunucu) revizyon farklılıklarını kontrol eder, güncelleme varsa bu değişiklikleri ayrıştırarak okunabilir log dosyaları ve özetler oluşturur.

## Özellikler
- **Otomatik Klasörleme:** Uygulama her çalıştığında `log-YYYY-MM-DD-HH-MM-SS` formatında anlık bir ana klasör oluşturur.
- **Özet (Summary) Raporları:** Projeye ait güncellemelerin, commit mesajlarının ve değişen dosyaların genel bir özeti `Proje_summary.txt` içerisine çıkarılır.
- **Detaylı (Diff) Log Ayrıştırma:** İçeriği değişen dosyalar tek bir dev log dosyasında tutulmaz; her dosya için kendi adıyla (`main_c_log.txt` vb.) ayrı dosyalar halinde ait olduğu alt klasörde saklanır.
- **Otomatik Mail Gönderimi:** Bütün raporlama bittikten sonra Outlook üzerinden önceden ayarlanmış adrese bilgi maili atar.

## Ayarlar (config.json)

Uygulamanın düzgün çalışabilmesi için `config.json` dosyasını kendi çalışma ortamınıza göre düzenlemelisiniz:

```json
{
  "output_dir": "",
  "paths": [
    "C:\\Projeler\\OrnekProje1",
    "C:\\Projeler\\OrnekProje2"
  ]
}
```

- **`output_dir`**: Rapor klasörlerinin (log-tarih-saat...) nereye kaydedileceğini belirler.
  - Eğer `""` şeklinde boş bırakılırsa, loglar uygulamanın `calistir.bat` dosyasının bulunduğu yerde oluşturulur.
  - Farklı bir yere çıkmasını isterseniz `C:\\Raporlarim` gibi bir yol yazabilirsiniz.
  - *Uyarı:* Windows'ta klasör yollarını yazarken aralardaki eğik çizgiyi çift ( `\\` ) koymanız gereklidir. (Örn: `C:\Users` yerine `C:\\Users`)

- **`paths`**: SVN kontrolünün yapılacağı projelerin yerel (bilgisayarınızdaki) dizinleridir. Alt alta istediğiniz kadar proje yolu ekleyebilirsiniz. (Yine çift eğik çizgi `\\` kullanmaya dikkat edin).

## Kullanım
İşlemleri başlatmak için `calistir.bat` dosyasına çift tıklamanız yeterlidir.
Açılan siyah ekranda işlemler tamamlandığında loglar belirttiğiniz konuma aktarılmış olacaktır.
