# Ortak backend kuralları

Kapsam HTTP API, worker ve servis backend'leridir. HTTP, kalıcı veri, mesajlaşma veya çok kiracılık gibi özelliklere bağlı kurallar yalnız ilgili projelerde uygulanır. Doğrulama sütunu, kuralın projede hangi kontrolle bağlanacağını belirtir; bu repoda o kontrollerin çalıştırıldığı anlamına gelmez.

## Mimari karar temeli

Sunum veya transport, iş kuralları ve veri erişimi sorumlulukları ayırt edilir. Bunun fiziksel karşılığı dile ve ihtiyaca göre değişir; sabit sayıda klasör, proje veya servis zorunlu değildir. [F01](sources.md#f01).

Basit kullanım senaryolarında Transaction Script; davranış ve invariant'ları yoğun modellerde Domain Model değerlendirilir. Repository, domain ile veri eşleme arasında faydalı bir sınır oluşturduğunda seçilir. Her entity için generic repository, CQRS, event sourcing veya mikroservis üretmek başlangıç şartı değildir. Bu tercih, Fowler'ın kataloğundaki alternatiflerin bu projeye uyarlanmasıdır. Repository girdisinin yazarları Edward Hieatt ve Rob Mee'dir. [F02](sources.md#f02), [F03](sources.md#f03), [F04](sources.md#f04), [F09](sources.md#f09).

## Kurallar

| Kimlik | Zorunluluk ve kapsam | Projede doğrulama | Dayanak |
| --- | --- | --- | --- |
| B01 | Kodlamadan önce dil, framework, sürümler, mimari kararlar ve gerekli kontroller proje profilinde belirlenir. Eksik veya örnek değerler hazır proje kabul edilmez. | Profil ve tasarım incelemesi; görev başlangıç kontrolü | Proje tercihi |
| B02 | Anlamlı iş kuralları HTTP handler veya controller'a gömülmez. SQL ve dış servis ayrıntıları belirlenen veri/entegrasyon sınırında tutulur. Modül bağımlılıkları açık olur. | İş kurallarını transport olmadan test et; yasak bağımlılıkları structural test veya analizle denetle | F01 |
| B03 | Modüller iş yetenekleri etrafında tanımlanır. Domain Model, Transaction Script, Repository ve servis sınırı seçimi gerekçelendirilir. Kullanılmayan soyutlama eklenmez. | Mimari karar kaydı ve bağımlılık incelemesi | F02–F04, F09; proje tercihi |
| B04 | Dış arayüzün girdi, çıktı, hata ve uyumluluk sözleşmesi bulunur. HTTP API için OpenAPI; başka protokol için uygun sözleşme seçilir. Liste, filtre, sıralama ve kaynak tüketimi sınırları belirlenir. | Sözleşme incelemesi ve API/contract testleri; kırıcı değişiklik kontrolü | Proje tercihi |
| B05 | Güvenilmeyen girdiler çalışma zamanında sınırda doğrulanır; tip kontrolü bunun yerine geçmez. İş invariant'ları yalnız UI veya transport doğrulamasına bırakılmaz. | Bozuk, eksik, aşırı büyük ve sınır değerli girdiler; iş kuralı testleri | S02, P02 |
| B06 | Kimlik ve kaynak bazlı yetki backend'de uygulanır. Çok kiracılık varsa tenant sınırı her ilgili erişimde korunur. Kullanıcının gönderdiği owner/tenant değeri tek başına yetki sayılmaz. | Kimliksiz, yetersiz yetkili, başka kullanıcıya/tenant'a ait kaynak senaryoları | S02 |
| B07 | Hatalar yutulmaz; iş hatası ile beklenmeyen hata sınırda eşlenir. REST/HTTP JSON API'de varsayılan hata gövdesi RFC 9457 Problem Details olur. Stack trace veya hassas ayrıntı dışarı verilmez. | Hata sözleşmesi, status ve hassas bilgi sızıntısı testleri | S01, S02; format seçimi proje tercihi |
| B08 | Kalıcı veri varsa transaction ve tutarlılık sınırı belirlenir. Bütünlük yalnız uygulama kontrolüne bırakılmaz; uygun veri kısıtları kullanılır. Tekrar eden ve eşzamanlı işlemlerin davranışı açıklanır. | Gerçek veri motoruyla rollback, constraint, tekrar ve ilgili concurrency testleri | Proje tercihi |
| B09 | Şema değişikliği sürümlü migration ile yapılır. Desteklenen önceki şemadan geçiş ve dağıtım uyumluluğu incelenir. Geri dönüş, gerektiğinde ileri düzeltme ve veri koruma planını içerir. | Boş veri tabanına kurulum ve önceki sürümden migration testi | Proje tercihi |
| B10 | Dış I/O için bağlantı/işlem zaman sınırları belirlenir. İptal uygun çağrı zincirine taşınır; kaynaklar doğru yaşam süresinde kapatılır. | Timeout, cancellation ve temizleme senaryoları | N03, N04, G06; ortaklaştırılmış proje kuralı |
| B11 | Retry yalnız güvenli/idempotent işlem veya tanımlı idempotency mekanizması için kullanılır; sayı, süre ve backoff sınırları bellidir. Tekrar çağrı çift yan etki üretmemelidir. | İlk deneme başarısızlığı, limit ve çift işlem senaryoları | Proje tercihi |
| B12 | Secret'lar ve hassas kişisel veriler kaynak koduna, test fixture'larına veya loglara yazılmaz. Kullanıcı girdileri SQL/komut/string birleştirmesiyle çalıştırılmaz; uygun parametrizasyon ve API'ler kullanılır. | Secret/static tarama ve ilgili enjeksiyon/log redaction testleri | S02 |
| B13 | Yapılandırılmış log ve istek/iş ilişkilendirmesi bulunur. Servisin hata ve gecikmesini anlamaya yetecek metrikler, gerektiğinde trace ve proje kalite hedefleri belirlenir. | Kontrollü hata isteğiyle log/telemetry incelemesi; seçilen hedeflere göre ölçüm | Proje tercihi |
| B14 | Gerekli konfigürasyon başlangıçta doğrulanır. Üretim ve test ayarları ayrılır. Para, zaman dilimi veya hassas sayı içeren alanda hassasiyet ve dönüşüm kuralları açıkça seçilir. | Eksik/yanlış ayarla başlangıç ve ilgili domain sınır testleri | Proje tercihi |
| B15 | Toolchain ve bağımlılık sürümleri kaydedilir. CI kilitli restore kullanır; doğrulama sırasında bağımlılıkları sessizce güncellemez. Desteklenen stable sürüm seçimi proje başında resmî destek bilgisiyle yapılır. | Temiz ortamda restore/build; lock ve çalışma ağacı fark kontrolü | P03, P07, N06, G02, G03 |
| B16 | Çalıştırılacak artifact, başlangıç ve kapanış davranışı tanımlıdır. Health/readiness kontrollerinin anlamı belgelenir; liveness uzak servis sağlığına körlemesine bağlanmaz. | Paketlenmiş artifact ile başlangıç, güvenli smoke ve graceful shutdown kontrolü | Proje tercihi |
| B17 | Değişiklik dar kapsamlı, anlaşılır ve refactoring'e elverişli olur. Hata düzeltmesi uygun regression testiyle korunur; test için gereksiz production soyutlaması üretilmez. | PR ve regression incelemesi | F05, F09, G01 |
| B18 | Bağımlılık ve güvenlik bulguları için tarayıcı, engelleme politikası ve süreli istisnalar belirlenir. Rapor üreten komut, tek başına güvenlik kapısının geçtiği kabul edilmez. | Politika eşiğini geçen örnek bulguda kontrolün başarısız olduğunu göster; gerçek raporu sakla | S02; kapı politikası proje tercihi |

## Projeye göre seçilecekler

Dil ve framework, ORM veya SQL aracı, authentication yöntemi, pagination biçimi, migration aracı, telemetry ürünü ve dağıtım ortamı bu metinle otomatik seçilmez. Proje profiline yazılır. Basit CRUD için zengin domain katmanları; tek servis için kuyruk, cache veya Kubernetes gerekliliği varsayılmaz.
