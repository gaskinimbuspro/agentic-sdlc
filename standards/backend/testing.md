# Backend test ve teslimat kuralları

Testler kabul kriterleri ve gerçek risklerden türetilir. Amaç, implementation'ın aynısını testte tekrar etmek veya her metot için test sayısını artırmak değildir. Kodun davranışını koruyan otomatik kontroller, geliştiricinin tamamlanma sorumluluğunun parçasıdır. [F05](sources.md#f05).

## Test kuralları

| Kimlik | Kural | Gerekli kanıt |
| --- | --- | --- |
| T01 | Her davranış değişikliği, riskine uygun otomatik doğrulamayla gelir. Önemsiz getter/DTO veya yalnız doküman değişikliğine yapay test eklenmez. | Görev kabul kriteri → test senaryosu ilişkisi |
| T02 | Anlamlı iş kuralı ve hata yolları transport'tan bağımsız unit/davranış testleriyle korunur. | Başarı, sınır değer, geçersiz durum ve ilgili hata testleri |
| T03 | Veri, HTTP veya kuyruk entegrasyonu varsa sınır gerçek uygulamayla sınanır. PostgreSQL yerine SQLite/in-memory testi, PostgreSQL integration kanıtı sayılmaz. | Aynı motor ve gerekli özelliklerle, projede sabitlenmiş sürümde integration raporu |
| T04 | API varsa gerçek routing, serialization, doğrulama, hata eşleme ve yetkilendirme zinciri sınanır. In-process test host'u uygundur; ağ ve paketlenmiş artifact ayrı kabul/smoke kontrolüdür. | API host testleri ve sürüme bağlı artifact kontrolü |
| T05 | Dış servis test double'ları unit ve dar integration testlerinde kullanılabilir. Sağlayıcıyla gerçek uyum ayrıca contract testi veya sandbox doğrulamasıyla gösterilir. | Double'ın kapsamı ve gerçek sınır doğrulamasının ayrı sonuçları |
| T06 | Test verisi izoledir; saat, rastgelelik, ağ ve ortak state kontrol edilir. Sabit sleep ile yarış gizlenmez; zaman sınırları bellidir. | Tek başına ve suit içinde tekrarlanabilir sonuç; fixture/cleanup düzeni |
| T07 | Hata düzeltmesinde mümkünse önce hatayı ortaya çıkaran regression testi gösterilir. Kritik invariant veya özel kontrol için negatif örnek ya da hedefli mutasyon kullanılır. | Düzeltme öncesi başarısızlık, sonrası başarı veya eşdeğer açıklanmış kanıt |
| T08 | Coverage eksik test alanlarını bulmak için kullanılır. Tek başına yüzde, kalite veya kabul kanıtı değildir. Gerekli test grubunda sıfır yürütülen test başarı sayılmaz. | Test sayıları, assertion'lar ve kritik davranış incelemesi; gerekiyorsa projeye özel eşik |
| T09 | Retry sonrası geçen kararsız test ve atlanan test görünür kalır. Zorunlu test karantinaya alınırsa gerekçe, sorumlu, süre ve telafi kontrolü kaydedilir; sessizce yeşile dönüştürülmez. | Passed/failed/skipped/flaky sayıları ve istisna kaydı |
| T10 | Her kontrolün gerçek komutu, exit code'u, test sayıları, commit/artifact kimliği ve ortamı kaydedilir. Çalıştırılamayan gerekli kontrol `blocked` olur; başarı uydurulmaz. | Makinece okunabilir rapor ve erişilebilir log/artifact bağlantısı |

Test doubles için [F07](sources.md#f07), coverage için [F06](sources.md#f06), sık ve otomatik geri bildirim için [F08](sources.md#f08) dayanak alınır. Bu tabloda belirlenen kapı ve kanıt politikaları bu standardın proje tercihleridir.

## Geçiş kapıları

| Kapı | Sorumluluk | Geçiş koşulu |
| --- | --- | --- |
| G0 Geliştirmeye hazır | Mimar/teknik sorumlu | Profil doldurulmuş; ilgili sözleşme, kabul kriterleri, modül/veri kararları ve gerekli test türleri belli |
| G1 Local doğrulama | Geliştirici | Format, statik kontrol, build/type check, ilgili unit testler ve değişikliğin gerektirdiği integration testleri başarılı |
| G2 Temiz ortamda CI | CI + geliştirici | Kilitli restore, format/static/build, gerekli bütün test grupları, sözleşme ve güvenlik kontrolleri başarılı; raporlar eksiksiz |
| G3 Bağımsız kabul | Doğrulayıcı | Beklentiler koddan kopyalanmadan gereksinimlerden değerlendirilmiş; test edilen commit/artifact belli; engelleyici bulgu yok |
| G4 Yayına hazır | Projenin yayın sorumlusu | Paketlenmiş artifact ile kritik akış ve güvenli smoke başarılı; migration ve geri dönüş yaklaşımı uygun |
| G5 Yayın sonrası | Operasyon/otomasyon | Yayına verilen sürümün güvenli smoke ve sağlık sinyalleri başarılı; belirlenen koşulda geri dönüş veya durdurma uygulanır |

Hızlı geri bildirim local ve erken CI aşamasında tutulur. Daha pahalı concurrency, güvenlik, performans veya mutation kontrolleri riskine göre sonraki zorunlu aşamalara yerleştirilir. PR kullanımı sık entegrasyonu engelleyecek uzun beklemelere dönüşmemelidir. [F08](sources.md#f08).

## Backend kabul senaryoları

Projede mevcut olan davranışlar için en az aşağıdaki riskler değerlendirilir:

- Geçerli istekte beklenen yanıt ve kalıcı yan etki.
- Eksik, bozuk, sınır dışı veya aşırı büyük girdide doğru hata ve istenmeyen yan etki oluşmaması.
- Kimliksiz, yetersiz yetkili ve başka kullanıcı/tenant'a ait kaynak erişimi. Kaynak varlığını gizleme dahil status politikası sözleşmede belirlenir.
- Transaction yarıda kaldığında veri tutarlılığı; constraint ve tekrar işlem davranışı.
- Bağımlılık timeout'u/iptalinde beklenen hata, sınırlı retry ve çift yan etki oluşmaması.
- Şema kurulumu, önceki desteklenen şemadan geçiş ve gerekli dağıtım uyumluluğu.
- Log ve hata yanıtında secret/hassas veri bulunmaması.
- Artifact başlangıcı, gerekli konfigürasyonun doğrulanması ve güvenli kapanış.

Mesajlaşma varsa duplicate delivery, acknowledge ve ilgili ordering; para veya stok gibi kritik domain varsa hassasiyet ve concurrency; özel parser/algoritma varsa property veya fuzz testleri ayrıca seçilir. Üretim müşteri verisi otomatik test fixture'ı olarak kullanılmaz.

## Kontrol sonucu sözleşmesi

Projede `backend-verify` alt kontrolleri sırayla yürütür, herhangi bir gerekli hata durumunda non-zero döner ve alt sonuçları kaydeder. Başarısız komutun sonucunu pipe, shell substitution, `continue-on-error` veya rapor parser'ı gizleyemez. Bazı runner'lar test bulamasa veya tarayıcılar bulgu üretse de exit 0 dönebilir; rapor içeriği ve test sayısı ayrıca kontrol edilir.

Sonuç en az şu alanları içerir: kural/kapı, komut, exit code, yürütülen/başarısız/atlanan test sayıları, commit veya image digest, redakte edilmiş ortam bilgisi, rapor bağlantısı, `passed/failed/blocked/not-applicable` durumu ve gerekçe. Gerekli kapılar tamamlanmadan birleştirme yapılmaması, projede CI ve repository korumalarıyla ayrıca uygulanır.
