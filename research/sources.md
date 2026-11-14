# Başlangıç kaynakları

Erişim tarihi: 14 Kasım 2026. Bu liste araştırma adaylarını ve ilk inceleme kapsamını kaydeder. Framework karşılaştırmaları tamamlanmadan uygulama sürümü seçilmez.

## Martin Fowler

Fowler'ın kendi makaleleri mühendislik ilkeleri, tasarım, test ve teslimat için başlangıç kaynaklarıdır.

- [The New Methodology](https://martinfowler.com/articles/newMethodology.html): Kısa iterasyonlarla öğrenme ve planı güncelleme.
- [Is Design Dead](https://martinfowler.com/articles/designDead.html): Evrimsel tasarımın test, CI ve refactoring ile ilişkisi.
- [Presentation Domain Data Layering](https://martinfowler.com/bliki/PresentationDomainDataLayering.html): Sunum, iş kuralları ve veri erişiminin ayrılması.
- [YAGNI](https://martinfowler.com/bliki/Yagni.html): Varsayılan gelecekteki ihtiyaçlar için eklenen karmaşıklığın maliyeti.
- [Monolith First](https://martinfowler.com/bliki/MonolithFirst.html): Başlangıçta servis sınırları ve mikroservis maliyetleri; 2015 tarihli değerlendirmesinin bağlamı korunmalı.
- [Self Testing Code](https://martinfowler.com/bliki/SelfTestingCode.html): Kodla birlikte gelişen otomatik testler.
- [Test Pyramid](https://martinfowler.com/bliki/TestPyramid.html), [Test Coverage](https://martinfowler.com/bliki/TestCoverage.html), [Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html): Test kapsamları, ölçümlerin sınırları ve test doubles.
- [Continuous Integration](https://martinfowler.com/articles/continuousIntegration.html), [Continuous Delivery](https://martinfowler.com/bliki/ContinuousDelivery.html): Sık entegrasyon, otomatik geri bildirim ve yayına hazır olma.
- [Agentic Engineering](https://martinfowler.com/bliki/AgenticEngineering.html): 21 Mayıs 2026 tarihli, insan sorumluluğu ve ajan çıktısının değerlendirilmesi üzerine yazı.

## SAP

[What Is Agentic Development](https://www.sap.com/turkey/resources/what-is-agentic-development): Hedef, görev planlama, araçlarla uygulama, geri bildirim ve insan incelemesi döngüsüne giriş. Ayrıntılı proje standardı olarak değil, kavram ve kapsam kaynağı olarak incelenir.

## BMad Method

- [Resmî repository](https://github.com/bmad-code-org/BMAD-METHOD)
- [UX ve mimari](https://docs.bmad-method.org/plan/design-ux-and-architecture/)
- [İşleri görevlere bölme](https://docs.bmad-method.org/plan/break-work-into-stories-and-track-it/)

İncelenen ana README, v6.12'yi stable ve ana branch'teki v7'yi preview alpha olarak tanımlıyordu. Release ile ana branch dokümanları karşılaştırmada ayrılmalı. İlk ilgi alanı; gereksinim, UX, mimari ve geliştirme oturumları arasında paylaşılan kararlardır.

## AWS AI DLC

- [Raja SP'nin yöntem tanıtımı](https://aws.amazon.com/blogs/devops/ai-driven-development-life-cycle/)
- [Uyarlanabilir workflow açıklaması](https://aws.amazon.com/blogs/devops/open-sourcing-adaptive-workflows-for-ai-driven-development-life-cycle-ai-dlc/)
- [Resmî repository](https://github.com/awslabs/aidlc-workflows)

Yaşam döngüsü, bağlama göre süreç derinliği ve insanın karar sorumluluğu incelenecek. Eski blog açıklamaları ile güncel repository sürümünün aşamaları birbirine karıştırılmayacak.

## GitHub Spec Kit

[Resmî repository](https://github.com/github/spec-kit): Proje ilkeleri, gereksinimler, teknik plan, görevler ve uygulama doğrulaması arasındaki ilişki incelenecek. README başlangıç incelemesinde okundu; deney öncesinde release veya commit sabitlenecek.

## Diğer yazarların çalışmaları

Fowler'ın sitesinde yayımlanmaları, bu makalelerin Fowler tarafından yazıldığı anlamına gelmez.

- [Birgitta Böckeler — Harness Engineering for Coding Agent Users](https://martinfowler.com/articles/harness-engineering.html): Ajanı yönlendiren rehberler ve çıktıyı değerlendiren kontroller.
- [Kief Morris — Humans and Agents in Software Engineering Loops](https://martinfowler.com/articles/exploring-gen-ai/humans-and-agents.html): Ürün amacı ile uygulama iş akışları üzerindeki insan sorumluluğu.
- [Rahul Garg — Patterns for Reducing Friction in AI Assisted Development](https://martinfowler.com/articles/reduce-friction-ai/): Bağlam aktarımı, tasarım görüşmesi ve takım standartları.
- [Naresh Jain — Are Harnesses Worth the Cost](https://martinfowler.com/articles/are-harnesses-worth-the-cost.html): Sınırlı bir görev üzerinde maliyet ve kabul sonucu karşılaştırması; genel üretim garantisi olarak yorumlanmamalı.
