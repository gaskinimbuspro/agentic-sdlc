# Go backend profili v0.1

Bu profil [ortak](../common.md) ve [test](../testing.md) kurallarına eklenir. Desteklenen stable Go toolchain sürümü proje başında seçilir. Standart kütüphaneyi kullanmak varsayılandır; ek framework veya DI kütüphanesi ihtiyaçla gerekçelendirilir.

| Kimlik | Kural | Doğrulama |
| --- | --- | --- |
| GO01 | `gofmt` zorunludur; paket adları açık ve kısa olur. Format kontrolü dosya değiştirerek geçmez; fark bulduğunda başarısız döner. | `gofmt -l` çıktısını denetleyen kapı |
| GO02 | Paketler anlamlı yetenek ve bağımlılık sınırlarıyla kurulur. `utils` içine iş davranışı yığılmaz; her entity için class/interface katmanları üretilmez. | Paket bağımlılığı incelemesi, gerekli structural test |
| GO03 | Normal iş hataları `error` ile döner. Hatalar kontrol edilir, bağlamla sarılır; kimlik gerektiğinde `errors.Is/As` ile değerlendirilir. String karşılaştırması ve normal hata için panic kullanılmaz. | Negatif senaryolar, vet ve kod incelemesi |
| GO04 | `context.Context` uygun çağrılarda ilk parametredir; deadline/cancellation alt I/O'ya taşınır. Context isteğe bağlı argüman çantası yapılmaz; genel olarak struct içine saklanmaz. | İptal/timeout testleri ve inceleme |
| GO05 | Interface gerektiğinde ve küçük tanımlanır; genellikle tüketen pakete aittir. Sırf mock üretmek için her somut tipe interface eklenmez. | Tüketici ve API tasarım incelemesi |
| GO06 | Goroutine'in sahibi, bitişi ve hata aktarımı bellidir. İş kapanırken goroutine/channel/timer yaşam süreleri yönetilir; shared state korunur. | Race detector ve ilgili shutdown/concurrency testleri |
| GO07 | `go.mod` ve gerekli `go.sum` kaydedilir. Tidy farkı ve readonly build/test ile bağımlılık sapması engellenir. CI kendiliğinden yeni toolchain indirmek yerine seçilen toolchain'i kullanır veya indirme politikasını açıkça sabitler. | Tidy diff, module verify, readonly build/test |
| GO08 | Standart `testing` ve HTTP sınırında `httptest` kullanılır; table-driven testler benzer senaryolarda tercih edilir. Gerekli suit'in gerçekten test yürüttüğü JSON olaylarından doğrulanır. | Unit/API/integration raporları ve yürütülen test sayısı |

Paket/interface/error için [G01](../sources.md#g01), dependency için [G02](../sources.md#g02), [G03](../sources.md#g03), race için [G04](../sources.md#g04), HTTP test için [G05](../sources.md#g05), context için [G06](../sources.md#g06), test altyapısı için [G07](../sources.md#g07) kullanılır. Feature düzeni ve araç varsayılanları bu standardın proje tercihleridir.

## Kontrol komutu şablonları

```sh
format_output="$(gofmt -l .)" || exit "$?"
test -z "$format_output"
go mod tidy -diff
go mod verify
go vet -mod=readonly ./...
go build -mod=readonly ./...
go test -mod=readonly -count=1 -json ./...
go test -mod=readonly -count=1 -tags=integration -json ./tests/integration/...
go test -mod=readonly -count=1 -race -json ./...
```

Her satır ayrı kontrol veya ilk hatada duran bir wrapper içinde çalıştırılır. `gofmt -l` tek başına fark bulunca non-zero dönmediğinden çıktı kontrolü gerekir. Hatalı gofmt çağrısının exit code'u da korunur.

Bu komut düzeninde gerçek bağımlılık testleri `tests/integration` altında ve `integration` build tag'iyle ayrılır; ilk `go test` onları çalıştırmaz. Projede farklı düzen seçilirse gerçek paket yolları profile yazılır. JSON çıktısını dosyaya aktaran runner, `go test` exit code'unu korumalı ve her gerekli grupta yürütülen testleri saymalıdır.

Race kontrolü desteklenen OS/architecture ve gerekli C toolchain ile CI'da çalışır. Desteklenmeyen local ortamda çalıştırılamaması `passed` sayılmaz; uygun runner'da tamamlanır. Race detector yalnız çalıştırılan yollardaki yarışları bulur; kritik concurrency senaryoları ayrıca tasarlanır. [G04](../sources.md#g04).
