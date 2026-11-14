# Araştırma planı

Amaç, mevcut agentic development yöntemlerini inceleyerek hedef gereksinimlerini karşılayan bir çalışma düzeni seçmek veya uyarlamaktır. Araştırma adım adım yürütülür; yalnız doküman okumakla uygulamadaki başarı eşit kabul edilmez.

## İnceleme sırası

1. Proje girdisi ve gereksinim hazırlama: Hangi bilgiler gerekiyor, eksikler nasıl ele alınıyor, başarı ölçütünü kim belirliyor?
2. Yaklaşım karşılaştırması: BMad Method, AWS AI-DLC ve GitHub Spec Kit aynı örnekle incelenir.
3. Mimari ve teknik profiller: Ortak ilkeler ile dil ve framework kuralları ayrılır; Python, .NET, Go ve UI profilleri araştırılır.
4. Test ve teslimat: Local geliştirme, CI, inceleme, kabul testleri, smoke, yayın ve geri dönüş koşulları incelenir.
5. Repo ve görev hazırlama: GitHub ayarları, görev şeması, gereksinim ilişkileri ve durum yönetimi belirlenir.
6. Ajan çalışma düzeni: Roller, araçlar, yetkiler, bağlam aktarımı, hata sonrası devam ve maliyet değerlendirilir.
7. Küçük deney: Önceden belirlenmiş aynı görev, sabitlenmiş yöntem sürümleri ve bağımsız kabul kriterleriyle sınanır.
8. Karar: Bulgular, alternatifler, maliyetler ve yeniden değerlendirme koşulları kaydedilir.

## Ortak karşılaştırma örneği

Henüz teknoloji seçmeden, kullanıcıların müşteri kaydı açıp listeleyebildiği bir API ve yönetim ekranı örneği hazırlanacak. Başlangıç dokümanı; kullanıcı rolleri, yetkilendirme, veri doğrulama, hata davranışı ve işletim beklentilerini açıklamaya yetecek ayrıntıyı taşımalı.

Yöntemlerin eksik gereksinimleri nasıl fark ettiği, hangi kararları insana bıraktığı ve görevlerin test edilebilirliğini nasıl sağladığı karşılaştırılacak. Mikroservis gerekliliği örneğe peşinen eklenmeyecek.

## Kaynak notu biçimi

Her not kaynak URL'sini, yazarı veya yayımlayan kurumu, yayın tarihini varsa, erişim tarihini ve incelenen sürümü içerir. GitHub kaynaklarında karşılaştırma için branch yerine mümkünse commit veya release sabitlenir.

Not içinde kaynak iddiası, dayanak türü, geçerli olduğu bağlam, karşı görüşler ve bizim çıkarımımız ayırt edilir. Tanıtıcı açıklama, uygulayıcı deneyimi ve deneysel sonuç aynı kanıt türü değildir.

## Bir karşılaştırmanın tamamlanması

- İncelenen sürümler ve birincil kaynaklar kaydedilmiş olmalı.
- Ölçütler aynı örnek üzerinden yanıtlanmış olmalı.
- Belgelenmiş özellik, ayrıca entegrasyon gerektiren özellik ve henüz doğrulanmamış özellik ayrılmalı.
- Maliyet, insan müdahalesi ve sınırlamalar görünür olmalı.
- Sonuç bir öneri içeriyorsa alternatifleri ve gerekçesi bulunmalı.

Araştırma sonucu tek başına kabul edilmiş standart değildir. Kabul edilen karar, gerekçesiyle birlikte ayrı bir karar kaydına dönüşür.
