# Python backend profili v0.1

Bu profil [ortak](../common.md) ve [test](../testing.md) kurallarına eklenir. Varsayılan araç tercihi uv, Ruff, mypy ve pytest'tir. Sürümleri proje başında sabitlenir. FastAPI, Django veya başka bir web framework'ü bu profil otomatik seçmez.

| Kimlik | Kural | Doğrulama |
| --- | --- | --- |
| PY01 | PEP 8'in okunabilirlik ve isimlendirme rehberi temel alınır. Ruff format ve lint kullanılır; bu profil için satır uzunluğu 88'dir. Ruff lint seçimi `E4,E7,E9,F,I,B,UP` olarak açıkça kaydedilir; tüm kuralların varsayılan açık olduğu sanılmaz. | Format ve lint kapıları; sabit araç/config sürümü |
| PY02 | Production fonksiyon ve arayüzlerinin tipleri tanımlıdır; `src` için mypy strict kullanılır. `Any` ve ignore'lar gerekçesiz yayılmaz. Type annotation'ın runtime validation sağlamadığı kabul edilir. | mypy; ayrıca bozuk API girdisi testleri |
| PY03 | `pyproject.toml`, desteklenen Python sürümü ve `uv.lock` bulunur. Varsayılan layout `src/<paket>` ve `tests/` olur; framework'ün farklı resmî düzeni seçilirse profil uyarlamasında açıklanır. Testler kurulmuş proje paketini kullanır. | Kilitli sync; doğru paketin import edildiği test ortamı |
| PY04 | İş kuralları framework request/response nesnelerine bağlanmaz. Web sınırında request/response doğrulaması ve exception eşlemesi framework'e uygun biçimde seçilir. | Transport'suz davranış ve gerçek app host testleri |
| PY05 | Async uygulamada event loop blocking I/O ile durdurulmaz. Desteklenen async API veya uygun worker sınırı kullanılır. İptal ve kaynak temizliği korunur; uzun işin yaşam süresi request'ten ayrılır. | Timeout/cancellation ve uygun concurrency senaryoları |
| PY06 | Beklenen hatalar tanımlı exception'larla aktarılır; geniş exception yakalama yalnız uygun sınırda, tekrar fırlatma/eşleme ve gözlemlenebilir sonuçla kullanılır. Bağlantı ve dosyalar context manager ile yönetilir. | Hata ve cleanup testleri; inceleme |
| PY07 | pytest ile unit, app/API ve gerçek bağımlılık testleri ayrılır. Yeni projede `--import-mode=importlib` kullanılır. Fixture state'i izole edilir; gerekli suit'te sıfır test geçiş sayılmaz. | Test raporu, pytest exit code ve yürütülen test sayısı |

PY01'in Ruff/88 seçimi ve PY02'nin strict seviyesi bu standardın tercihleridir. İsimlendirme ve typing için [P01](../sources.md#p01), [P02](../sources.md#p02); paketleme için [P03](../sources.md#p03); araçlar için [P04](../sources.md#p04), [P05](../sources.md#p05), [P06](../sources.md#p06), [P07](../sources.md#p07) kullanılır.

## Kontrol komutu şablonları

Proje kökünde çalışacak örnek komutlar aşağıdadır. `tests/unit` ve `tests/integration` gerçek, ilgili testleri içermelidir. Integration kapsamı yoksa gerekçesi proje profilinde kaydedilir; boş suit'e sahte test eklenmez.

```sh
uv sync --locked --group dev
uv run --no-sync ruff format --check .
uv run --no-sync ruff check .
uv run --no-sync mypy --strict src
uv run --no-sync python -m pytest --import-mode=importlib tests/unit --junitxml=artifacts/unit.xml
uv run --no-sync python -m pytest --import-mode=importlib tests/integration --junitxml=artifacts/integration.xml
```

`dev` dependency group araçları ve tip stub'larını içermeli; `src` düzeni kullanılıyorsa build backend ve paket kurulumu yapılandırılmalıdır. Python/uv sürümü proje kaydında, test/lint araçları lock içinde sabitlenir. `--no-sync`, önceden başarılı kilitli sync adımına dayanır. Her komut ayrı kontrol edilir; ilk hata sonraki komutun exit code'u ile gizlenmez.

Framework test host'u, lifespan/startup, runtime validation, migration ve gerçek bağımlılık fixture'ları proje profilinde ayrıca seçilir. Bu şablon tek başına uygulama veya CI oluşturmaz.
