# Backend standardı v0.1

Bu standart, yeni bir projede backend geliştiren ve doğrulayan ajanların uyması için hazırlanmış ilk sürüm taslağıdır. Ortak kurallar, seçilen dil profili ve projeye özel framework kararları birlikte uygulanır. Başlangıç kapsamı Python, C#/.NET ve Go'dur; başka bir dil seçilirse önce onun profili eklenir.

## Standart bileşenleri

| Belge | Belirlediği konu |
| --- | --- |
| [Ortak backend kuralları](common.md) | Mimari, API, güvenlik, veri, hata ve işletim beklentileri |
| [Test ve teslimat kuralları](testing.md) | Geliştiriciden kabul ve smoke kontrollerine kadar doğrulama |
| [Python profili](profiles/python.md) | Paketleme, typing, biçim, lint ve pytest |
| [.NET profili](profiles/dotnet.md) | Nullable, analyzer, DI, async ve test düzeni |
| [Go profili](profiles/go.md) | Paketler, interface, error, context ve concurrency |
| [Ajan çalışma sözleşmesi](agent-contract.md) | Mimar, geliştirici ve doğrulayıcının girdileri ve çıktıları |
| [Proje profili şablonu](project-profile.template.json) | Projede kullanılacak sürümler, kararlar ve gerçek kontrol komutları |
| [Kaynaklar ve atıf sınırları](sources.md) | Her yaklaşımın dayanağı ve bizim araç tercihlerimiz |

## Kuralların anlamı

Bu sürümü benimseyen bir projede uygulanabilir B, T ve seçilen dilin PY, NET veya GO kuralları zorunludur. Koşullu bir kural yalnız belirtilen durum varsa uygulanır. Örneğin veritabanı olmayan bir servise migration altyapısı eklenmez; para işleyen serviste para hassasiyeti ve tekrar işlem senaryoları atlanmaz.

Bir kuralın uygulanmaması; gerekçe, risk, telafi kontrolü, karar veren kişi veya rol ve yeniden değerlendirme tarihiyle kaydedilir. Ajan, kontrolü geçirmek için kuralı veya test kapsamını sessizce gevşetemez. Eski bir kod tabanına geçişte mevcut ihlaller ayrıca listelenir; yeni ihlaller gizlenmez.

Fowler'ın mimari ve test ilkeleri ile dil rehberleri ayrı kaynaklardır. Ruff, uv, mypy, pytest, xUnit, 88 karakter gibi seçimler bu taslağın proje tercihleridir; Fowler'ın veya dilin zorunlu tuttuğu evrensel standartlar değildir.

## Yeni projede uygulama sırası

1. Mimar rolü ortak kuralları ve uygun dil profilini okur; [proje profili şablonunu](project-profile.template.json) proje için doldurur.
2. Framework ve sürümler, modül sınırları, veri yaklaşımı, API sözleşmesi ve gereken test senaryoları belirlenir. Belirsizlikler çözülmeden proje hazır sayılmaz.
3. Dil profilindeki komutlar gerçek proje yollarına ve sabitlenmiş araçlara bağlanır. Framework'ün doğrulama, hata eşleme, test host'u ve yaşam döngüsü davranışı ayrıca belirtilir.
4. Projede `backend-verify` adlı tek bir doğrulama giriş noktası ve onu çalıştıran zorunlu CI kontrolü oluşturulur. Alt kontrollerin sonuçları ve test sayıları ayrı görünür kalır.
5. Geliştirici ve doğrulayıcı, [test kapıları](testing.md) ile çalışır; gerekli kontroller başarısız, eksik veya engelliyse iş tamamlanmış sayılmaz.

## Mevcut uygulama durumu

Bu repo standart metinlerini, komut şablonlarını ve örnek proje profili yapısını içerir. Henüz bu standardı uygulayan bir backend, genel amaçlı profil doğrulayıcısı veya çalışan `backend-verify` pipeline'ı içermez. Bir proje bu standardı aldığında kontrollerin gerçek kod üzerinde kurulması ve kırılabildiğinin gösterilmesi gerekir. Yalnız Markdown talimatı, erişim veya CI koruması sağlamaz.

## Sürümleme

Projeler `backend_standard` alanıyla kullandıkları sürümü kaydeder. Standart güncellemesi, projelerdeki davranışı kendiliğinden değiştirmez; sürüm geçişi uyumluluk ve kontrol değişiklikleriyle ele alınır. Taslak v0.1'in örnek projede uygulanması ve geri bildirimle gözden geçirilmesi sonraki adımdır.
