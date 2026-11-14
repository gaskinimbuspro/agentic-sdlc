# Backend için ajan çalışma sözleşmesi

Bu sözleşme sorumlulukları tanımlar; belirli model sağlayıcısı veya ayrı çalışan ajan sayısı seçmez. Aynı kişi veya araç farklı oturumlarda birden fazla rolü üstlenebilir. Bağımsız doğrulamada beklentiler, geliştiricinin varsayımlarından ayrı olarak gereksinimlerden okunur.

## Her görevin girdisi

- Görev ve kabul kriterleri; ilgili gereksinim kimlikleri.
- Backend standardı sürümü, [ortak kurallar](common.md), [test kuralları](testing.md) ve seçilen [dil profili](README.md).
- Doldurulmuş proje profili; framework, API/veri ve mimari kararları.
- Yetkili çalışma alanı, araçlar ve mevcut kod tabanının kuralları.

## Mimar veya teknik sorumlu

Projeye uygun dili ve framework'ü gerekçelendirir; sürümleri resmî destek bilgisiyle seçer. Basit işlem akışı ile yoğun domain davranışını ayırır. Modül, API, veri ve transaction sınırlarını; hata, iptal ve tekrar davranışlarını belirler. Bu kararların profile ve test senaryolarına taşındığını doğrular. Gereksiz Repository, CQRS, mikroservis veya kuyruk eklemez.

Çıktı: hazır proje profili, ilgili karar kaydı, sözleşme ve görevle ilişkili test beklentileri. Şablonu kopyalamak veya `readiness` değerini değiştirmek tek başına hazırlık kanıtı değildir.

## Geliştirici

Göreve başlamadan önce girdileri okur. Mevcut proje seçimini gerekçesiz değiştirmez. Kodu seçilen profile göre yazar; davranış ve hata senaryolarını test eder; G1 kontrollerini gerçek hedef kod üzerinde çalıştırır. Testi geçirmek için kabul kriterini, assertion'ı, kuralı veya güvenlik kontrolünü zayıflatmaz. Eksik bağımlılık/erişim nedeniyle kontrol çalışmıyorsa bunu `blocked` olarak bildirir.

Çıktı: dar kapsamlı değişiklik, ilgili testler, gerçek komut sonuçları ve PR. Başarısızlıkları ve bilinen açıkları raporlar.

## Doğrulayıcı

Kabul kriterlerini ve ilgili standardı okuyarak API, iş kuralı, veri ve güvenlik davranışını değerlendirir. Yalnız test sayısına veya geliştirici ajanının başarı beyanına dayanmaz. Gerektiğinde eksik negatif senaryo ve entegrasyon kanıtını ister; bulguyu somut tetikleyici, etki ve ilgili kuralla açıklar.

Çıktı: bulgular, doğrulanan sürüm, çalıştırılmış kontroller ve açık/çözülmüş durumları. Mimarın seçtiği çözüm ile standarda aykırılığı birbirinden ayırır; kişisel üslup tercihlerini engelleyici bulgu yapmaz.

## Kontrollerin kurulması

Proje hazırlanırken komutlar gerçek yollarla doldurulur, toolchain sabitlenir ve `backend-verify` giriş noktası CI'a bağlanır. Yeni bir kalite kapısının yalnız başarılı yolu değil, ilgili hatayı engellediği de kasıtlı bir negatif örnekle gösterilir. Deneme değişikliği geri alınır; hangi hatanın yakalandığı kanıta eklenir. Bu repodaki doküman kontrolü, Python/.NET/Go backend testlerinin çalıştırıldığı anlamına gelmez.

## Başlangıç talimatı örneği

> Bu backend görevinde backend standardı v0.1'i uygula. Önce ortak kuralları, test kurallarını, seçilen dil profilini ve proje profilini oku. Eksik mimari veya test kararlarını belirt. Hazır olduğunda yalnız görev kapsamını geliştir; gerekli kontrolleri çalıştır ve komut, exit code, test sayıları, commit/artifact ve kanıtları raporla. Kontrol çalışmadıysa başarı beyan etme.
