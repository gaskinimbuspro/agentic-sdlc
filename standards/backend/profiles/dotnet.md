# C# and .NET backend profile v0.1

Apply with [common](../common.md) and [testing](../testing.md) rules. Select a supported stable SDK/target framework and record the SDK in `global.json`. Justify Minimal API versus controllers; there is no fixed project-count requirement.

The executable [ASP.NET Core binding](../../../reference/README.md) uses a pinned .NET 10 LTS SDK, nullable/analyzer enforcement, locked NuGet restore, xUnit/VSTest, and published-assembly HTTP/PostgreSQL acceptance in CI.

| ID | Rule | Verification |
| --- | --- | --- |
| NET01 | Configure `.editorconfig` and analyzers. Enable nullable analysis; treat compiler/analyzer warnings as errors in new projects and connect selected style rules to checks. | Format verification and analyzer/warning-as-error build |
| NET02 | Separate API DTO, business behavior, and persistence responsibilities. Do not expose EF entities accidentally or require generic Repository/MediatR for every service. | Contract and dependency review |
| NET03 | Respect DI lifetimes. Do not capture scoped services in singletons or hide dependencies behind service location. Respect DbContext scope/concurrency limits. | Scope validation, app startup, and lifecycle tests |
| NET04 | Use async I/O where supported; avoid `.Result`, `.Wait()`, and request `async void`. Propagate CancellationToken to appropriate dependencies. | Analysis/review and cancellation/timeout tests |
| NET05 | Manage HTTP client lifetimes; default to IHttpClientFactory. Avoid uncontrolled per-request clients and dispose resources correctly with using/await using. | Client registration and cleanup checks |
| NET06 | Enable NuGet locks, commit `packages.lock.json`, and use locked restore in CI. | Clean restore and lock-diff checks |
| NET07 | Default to xUnit with the VSTest command profile. Exercise actual middleware/routing through WebApplicationFactory or a packaged HTTP process; use the real data engine for persistence behavior. | Separate unit/integration reports and T03/T04 |

Sources: [N01](../sources.md#n01), [N02](../sources.md#n02), [N03](../sources.md#n03), [N04](../sources.md#n04), [N05](../sources.md#n05), [N06](../sources.md#n06). xUnit/VSTest are this draft's choices. MTP uses different CLI behavior and requires an adapted command profile. [N08](../sources.md#n08).

## Command templates

Service paths below are examples, not applications in this standards repository. Record actual solution/test paths in the project profile.

```sh
dotnet restore --locked-mode
dotnet format --verify-no-changes --no-restore
dotnet build --configuration Release --no-restore -warnaserror
dotnet test tests/Service.UnitTests/Service.UnitTests.csproj --configuration Release --no-build --no-restore --logger "trx;LogFileName=unit.trx"
dotnet test tests/Service.IntegrationTests/Service.IntegrationTests.csproj --configuration Release --no-build --no-restore --logger "trx;LogFileName=integration.trx"
```

The solution must include/build test projects. Pin test SDK/adapter, framework, analyzers, and formatter. Control runner-selection environment settings. Verify executed tests in TRX even if the command returns zero. Add checks for custom policies outside formatter coverage. [N07](../sources.md#n07), [N08](../sources.md#n08).
