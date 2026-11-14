# Hedef ve gereksinimler

Bu çalışma, Gökhan'ın yeni projelerini ajanlarla hazırlayıp geliştirmesi için tekrar kullanılabilir bir agentic SDLC çatısını tanımlar. Proje başlangıcında aynı mühendislik kararlarını ve çalışma kurallarını yeniden keşfetme ihtiyacını azaltmayı amaçlar.

## Kullanım senaryosu

Gökhan bir API, UI ve backend uygulaması veya birden çok servisten oluşan ürün fikrini ayrı bir proje dokümanında açıklar. Çatı bu dokümanı inceler, eksikleri ve varsayımları belirler, gereksinimleri netleştirir ve uygun çözümü tasarlamaya yardımcı olur. Tasarımdan geliştirilmeye hazır görevler çıkarır; yetkisi ve araçları varsa repository ile görev takip hazırlığını yapar.

İnsan, ürün öncelikleri ve önemli tasarım kararlarında sorumluluğu korur. Ajanlar tanımlı yetki, standart ve doğrulama kuralları içinde çalışır.

## Gereksinimler

| Kimlik | Gereksinim |
| --- | --- |
| R01 | Proje fikrinden kullanıcı senaryoları, kapsam, kapsam dışı işler ve kabul kriterleri çıkarılmalı; önemli eksikler görünür olmalı. |
| R02 | Ortak standartlar, çalışma ayarları ve projeye özel gereksinimler ayrı yönetilmeli. |
| R03 | Backend ve UI için kaynaklara dayanan mühendislik standartları bulunmalı. |
| R04 | Projeye uygun dil ve framework seçimi gerekçelendirilmeli; Python, .NET ve Go için ayrı profiller araştırılmalı. |
| R05 | Seçilen profillerin kuralları geliştirmenin tamamında uygulanmalı; standart değişikliği gerekçesiyle izlenmeli. |
| R06 | Mimari; servis sınırları, veri sahipliği, API sözleşmeleri, güvenlik, işletim ve UI akışlarını projenin ihtiyacı kadar kapsamalı. |
| R07 | Rol sorumlulukları, girdiler, çıktılar, araçlar ve devir koşulları açık olmalı. Ajan sayısı araştırma sonucunda belirlenmeli. |
| R08 | GitHub hesabı veya organizasyonu, repository isimlendirmesi, görünürlüğü, mono/multi-repo seçimi ve başlangıç kontrolleri tanımlanmalı. |
| R09 | Görevler gereksinimlere bağlanmalı; kapsam, bağımlılıklar, kabul kriterleri, ilgili kararlar ve doğrulama beklentileri içermeli. |
| R10 | Geliştiricinin local doğrulaması, CI, bağımsız inceleme, test ortamı, smoke ve yayın sonrası kontrollerin sorumlulukları açıklanmalı. |
| R11 | Çalıştırılan kontrollerin gerçek sonuçları, ilgili commit veya artifact ve kanıtları izlenmeli. Çalıştırılamayan kontroller başarılı gösterilmemeli. |
| R12 | Durum ve bağlam farklı oturumlara aktarılabilmeli; tekrar denemeler gereksiz repo, issue veya PR kopyaları üretmemeli. |
| R13 | Ortak çatı geliştikçe projelerin hangi sürümü kullandığı ve nasıl güncelleneceği belirlenmeli. |

## Başlangıçta belirlenen tercihler

- Hedef GitHub hesabı: `gaskinimbuspro`.
- Ana repository: `gaskinimbuspro/agentic-sdlc`.
- Mevcut repository görünürlüğü: public.
- Mevcut çalışma aşaması: araştırma; ürün geliştirme veya workflow kurulumu değil.
- Bu çalışmanın görev takibi: GitHub.
- Ana çatının her proje için başvurulan çalışma temeli olması; projeye özel dokümanın ayrı hazırlanması.

## Araştırmayla netleşecek kararlar

Framework seçimi, ajan rolleri ve sayısı, teknik profiller, proje girdi şablonu, repo oluşturma politikası, görev şeması, test kapıları ve otomasyonun nasıl çalıştırılacağı henüz belirlenmedi. MCP, n8n veya Jira gerekliliği peşinen varsayılmayacak.

GPU, Kubernetes ve RAG konuları ilerleyen aşamalarda uygulama ve altyapı profilleri olarak ele alınabilir. İlk araştırma bunlara ihtiyaç duymayan projelerde de kullanılabilecek geliştirme temelini inceler.
