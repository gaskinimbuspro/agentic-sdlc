# C# ve .NET backend profili v0.1

Bu profil [ortak](../common.md) ve [test](../testing.md) kurallarına eklenir. Desteklenen stable SDK ve target framework proje başlangıcında seçilir; SDK `global.json` ile kaydedilir. Minimal API veya controller seçimi gerekçelendirilir; sabit sayıda solution projesi şartı yoktur.

| Kimlik | Kural | Doğrulama |
| --- | --- | --- |
| NET01 | `.editorconfig` ve .NET analyzer politikası bulunur. Nullable açık olur; yeni projede compiler/analyzer uyarıları kontrolsüz bırakılmaz. Seçilen stil kuralları build/format kontrolüne bağlanır. | Format doğrulaması; analyzer ve warning-as-error build |
| NET02 | DTO, iş davranışı ve persistence sorumlulukları ayrılır. EF Core entity'si dış API sözleşmesi yerine gelişigüzel kullanılmaz. Generic Repository veya MediatR her projeye zorunlu eklenmez. | API sözleşmesi ve bağımlılık incelemesi |
| NET03 | DI yaşam süreleri doğrudur. Scoped bağımlılık singleton'da tutulmaz; service locator ile bağımlılık gizlenmez. `DbContext` varsa request/job scope'u ve eşzamanlı kullanım sınırı korunur. | Scope validation, test host başlangıcı ve ilgili yaşam süresi testleri |
| NET04 | Uygun I/O zinciri async olur; `.Result`, `.Wait()` ve request içinde `async void` kullanılmaz. `CancellationToken` uygun alt çağrılara taşınır. | Analyzer/inceleme; timeout/cancellation senaryoları |
| NET05 | HTTP istemcisi yaşam süresi yönetilir; varsayılan seçim `IHttpClientFactory` olur. Her request için kontrolsüz `new HttpClient` üretilmez. `IDisposable/IAsyncDisposable` kaynaklar uygun `using/await using` ile temizlenir. | İstemci kaydı ve cleanup testleri/inceleme |
| NET06 | NuGet lock kullanımı etkinleştirilir; `packages.lock.json` kaydedilir ve CI `--locked-mode` restore yapar. | Temiz restore; lock değişiklik kontrolü |
| NET07 | Varsayılan test framework'ü xUnit, komut profili VSTest'tir. API integration testleri `WebApplicationFactory` ile gerçek pipeline'ı kullanır; DB davranışında gerçek veri motoru ayrıca sağlanır. | Unit ve integration projelerinin ayrı raporları; T03/T04 |

Kodlama ve nullable için [N01](../sources.md#n01), [N02](../sources.md#n02); async/HTTP için [N03](../sources.md#n03); DI için [N04](../sources.md#n04); integration için [N05](../sources.md#n05); lock için [N06](../sources.md#n06) dayanak alınır. xUnit ve VSTest bu taslağın araç tercihleridir. Test runner seçimi CLI seçeneklerini etkiler; MTP seçilirse bu komut profili ayrıca uyarlanır. [N08](../sources.md#n08).

## Kontrol komutu şablonları

Gerçek solution ve test proje yolları proje profilinde belirlenir. Aşağıdaki `Service.*` yolları örnektir; bu standart reposunda mevcut backend projeleri değildir.

```sh
dotnet restore --locked-mode
dotnet format --verify-no-changes --no-restore
dotnet build --configuration Release --no-restore -warnaserror
dotnet test tests/Service.UnitTests/Service.UnitTests.csproj --configuration Release --no-build --no-restore --logger "trx;LogFileName=unit.trx"
dotnet test tests/Service.IntegrationTests/Service.IntegrationTests.csproj --configuration Release --no-build --no-restore --logger "trx;LogFileName=integration.trx"
```

Solution bütün test projelerini içermeli; build onları da üretmelidir. Test SDK/adapter, xUnit, analyzer ve formatter sürümleri sabitlenir. CI'da runner seçimini değiştiren ortam ayarları kontrol edilir. `dotnet test` exit 0 olsa bile gerekli suit'in gerçekten test yürüttüğü TRX sonuçlarından doğrulanır. Format komutunun denetlemediği özel kurallar ayrıca kontrol edilir. [N07](../sources.md#n07), [N08](../sources.md#n08).
