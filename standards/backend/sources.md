# Backend standardının kaynakları

Erişim tarihi 14 Kasım 2026. İlgili resmî sayfalar ve yazarların kendi metinleri incelendi. Bu kaynaklar tek bir ortak backend reçetesi yayımlamaz; standardın kuralları onlardan yapılan, açıkça belirtilmiş proje seçimlerini de içerir. Komut ve strict/analyzer seçenekleri araç sürümleriyle değişebileceği için projede sürüm sabitleme gerekir.

## F01

Martin Fowler, [Presentation Domain Data Layering](https://martinfowler.com/bliki/PresentationDomainDataLayering.html). Sunum, domain ve veri erişimini ayırma; mantıksal katman ile fiziksel servis sayısını eşitlememe.

## F02

Martin Fowler, [Transaction Script](https://martinfowler.com/eaaCatalog/transactionScript.html). İstek etrafında prosedürel iş akışı, basit backend için incelenebilecek domain logic yaklaşımıdır.

## F03

Martin Fowler, [Domain Model](https://martinfowler.com/eaaCatalog/domainModel.html). Veriyle birlikte davranışı modelleme. Bütün CRUD uygulamalarına zorunlu model olarak aktarılmaz.

## F04

Edward Hieatt ve Rob Mee, Fowler'ın kataloğunda [Repository](https://martinfowler.com/eaaCatalog/repository.html). Domain ve veri eşleme arasında koleksiyon benzeri sınır. Generic Repository'yi her projeye ekleme zorunluluğu bu kaynaktan çıkarılmaz.

## F05

Martin Fowler, [Self Testing Code](https://martinfowler.com/bliki/SelfTestingCode.html). Kodla birlikte gelişen otomatik testler ve güvenli değişiklik. TDD ile self-testing code aynı kavram değildir.

## F06

Martin Fowler, [Test Coverage](https://martinfowler.com/bliki/TestCoverage.html). Coverage eksik alanları bulmaya yardımcıdır; yüksek sayı yeterli test kalitesini göstermez.

## F07

Martin Fowler, [Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html). Test doubles, state/behavior verification ve test yaklaşımlarının ayrımı. Toptan mock yasağına dayanak yapılmaz.

## F08

Martin Fowler, [Continuous Integration](https://martinfowler.com/articles/continuousIntegration.html). Sık entegrasyon, otomatik build/test, hızlı geri bildirim ve aşamalı kontroller. CI servisinin yalnız branch üzerinde çalışması tanım için yeterli değildir.

## F09

Martin Fowler, [YAGNI](https://martinfowler.com/bliki/Yagni.html). Varsayılan gelecek ihtiyaçları için eklenen karmaşıklık ile değiştirilebilirliği koruyan refactoring/test yatırımının ayrılması.

## S01

IETF, [RFC 9457 Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457.html). HTTP API hata ayrıntısı biçimi. Bunun REST JSON API'lerde varsayılan seçilmesi bizim standardımızın kararıdır.

## S02

OWASP, [Application Security Verification Standard](https://asvs.owasp.org/). Güvenlik gereksinimi ve doğrulama çerçevesi. Bütün ASVS maddelerine uyum veya sertifikasyon iddia edilmez; projede uygulanabilir maddeler ve tarama politikası seçilir.

## P01

Python, [PEP 8](https://peps.python.org/pep-0008/). Okunabilirlik, isimlendirme ve stil. Bu taslaktaki Ruff/88 karakter seçimi PEP 8'in evrensel zorunluluğu değildir.

## P02

Python, [typing](https://docs.python.org/3/library/typing.html). Type annotation'lar runtime'da otomatik uygulanmaz; çalışma zamanı doğrulaması ayrıca gerekir.

## P03

PyPA, [Writing your pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/). Proje metadata'sı, bağımlılıklar ve araç konfigürasyonu. uv veya src düzeni seçimi bu standardın varsayılanıdır.

## P04

Astral, [Ruff formatter](https://docs.astral.sh/ruff/formatter/) ve [Ruff linter](https://docs.astral.sh/ruff/linter/). Format check, lint seçimi ve farklı exit code'lar. Lint grubunun açıkça seçilmesi gerekir.

## P05

mypy, [Command line](https://mypy.readthedocs.io/en/stable/command_line.html). Strict seçenekleri; strict kapsamı sürümle değişebilir ve bütün olası analizleri kapsamaz.

## P06

pytest, [Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html) ve [Exit codes](https://docs.pytest.org/en/stable/reference/exit-codes.html). Paket/import düzeni, importlib modu ve test bulunmaması dahil çıkış durumları.

## P07

Astral uv, [Locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/). Kilitli doğrulama ve otomatik sync davranışı. uv bu standardın paket yöneticisi tercihidir.

## N01

Microsoft, [.NET Coding Conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions). C# kodlama rehberi; projenin analyzer ve style ayarlarına temel sağlar.

## N02

Microsoft, [Nullable reference types](https://learn.microsoft.com/en-us/dotnet/csharp/nullable-references). Nullability analizi. Nullable'ı zorunlu etkinleştirmek bu profilin seçimidir.

## N03

Microsoft, [ASP.NET Core Best Practices](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/best-practices). Async I/O, bloklayan çağrılar, HttpClient ve request yaşam süresiyle ilgili öneriler.

## N04

Microsoft, [Dependency injection guidelines](https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection-guidelines). DI yaşam süreleri ve kaynakların temizlenmesi. Bütün saf nesneler için DI zorunluluğu çıkarılmaz.

## N05

Microsoft, [Integration tests in ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/testing/integration-testing). WebApplicationFactory ve test host'u. In-memory test host'u ile gerçek veri motoru kullanımı farklı kararlardır.

## N06

Microsoft NuGet, [Locking dependencies](https://learn.microsoft.com/en-us/nuget/consume-packages/package-references-in-project-files#locking-dependencies). Lock dosyası ve `dotnet restore --locked-mode` davranışı.

## N07

Microsoft, [dotnet format](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-format). Format/analyzer seçenekleri ve verify-no-changes kontrolü.

## N08

Microsoft, [dotnet test](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test). VSTest/MTP seçimiyle komut seçenekleri ve davranış değişir. xUnit + VSTest bu taslağın tercihidir; test sayısı kontrolü ek kapı gereksinimidir.

## G01

Go, [Code Review Comments](https://go.dev/wiki/CodeReviewComments). Paket, interface, context ve hata pratikleri. Interface'in çoğunlukla tüketicide tanımlanması ve sırf mock için eklenmemesi ele alınır.

## G02

Go, [Managing dependencies](https://go.dev/doc/modules/managing-dependencies). Modules ile bağımlılık yönetimi.

## G03

Go, [Modules Reference](https://go.dev/ref/mod). Tidy diff ve readonly module davranışı. `go mod tidy -diff` fark varsa non-zero döner ve dosyaları değiştirmez.

## G04

Go, [Data Race Detector](https://go.dev/doc/articles/race_detector). `-race`, çalıştırılmış kod yollarındaki veri yarışlarını bulur; platform ve toolchain gereksinimleri vardır.

## G05

Go standard library, [net/http/httptest](https://pkg.go.dev/net/http/httptest). HTTP handler/server test araçları.

## G06

Go standard library, [context](https://pkg.go.dev/context). Deadline ve iptal sinyallerinin API sınırlarında taşınması.

## G07

Go standard library, [testing](https://pkg.go.dev/testing). Go test altyapısı. Gerekli test gruplarında sıfır yürütülen testi engellemek bu standardın ek kontrolüdür.
