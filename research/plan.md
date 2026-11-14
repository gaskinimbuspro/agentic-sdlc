# Araştırma planı

Amaç, mevcut agentic development yöntemlerini inceleyerek hedef gereksinimlerini karşılayan bir çalışma düzeni seçmek veya uyarlamaktır. Araştırma adım adım yürütülür; yalnız doküman okumakla uygulamadaki başarı eşit kabul edilmez.

## İnceleme sırası

1. Backend ortak kuralları: Fowler'ın mimari ve test ilkeleri, güvenlik ve API sözleşmeleri.
2. Dil profilleri: Python, .NET ve Go için resmî rehberler, araç seçimleri ve doğrulama komutları.
3. Backend test kapıları: Local, CI, bağımsız kabul ve smoke; gerçek kanıt ve başarısızlık koşulları.
4. Küçük backend deneyi: Seçilen profili gerçek örneğe bağla; zorunlu kontrollerin ihlalde kırıldığını göster ve v0.1'i gözden geçir.
5. Proje girdisi ve yöntem karşılaştırması: Aynı örnek proje dokümanını BMad Method, AWS AI-DLC ve GitHub Spec Kit ile incele.
6. UI standardı: Kullanıcı akışları, component düzeni, erişilebilirlik ve UI testlerini belirle.
7. Repo, görev ve ajan düzeni: GitHub ayarları, görev sözleşmesi, roller, yetkiler ve bağlam aktarımı.
8. Karar ve yaygınlaştırma: Deney sonuçlarını, maliyeti, standart sürümlerini ve geçiş koşullarını kaydet.

Öncelik backend standardıdır. Diğer başlıklar korunur; ilk backend sürümü denenmeden orkestrasyon seçimi veya ürün uygulaması tamamlanmış sayılmaz.

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
