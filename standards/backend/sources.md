# Sources for the backend standard

Accessed 14 November 2026. Official documentation and authors’ own public text were inspected. These sources do not jointly publish one backend recipe. Tool choices, mandatory gates, task isolation, and completion policy remain our explicit decisions. Pin versions because command behavior changes.

## F01

Martin Fowler, [Presentation Domain Data Layering](https://martinfowler.com/bliki/PresentationDomainDataLayering.html). Separate presentation, domain behavior, and data access. Logical layers do not imply separate deployed services.

## F02

Martin Fowler, [Transaction Script](https://martinfowler.com/eaaCatalog/transactionScript.html). Procedural domain logic organized around requests is a candidate for simple workflows.

## F03

Martin Fowler, [Domain Model](https://martinfowler.com/eaaCatalog/domainModel.html). Model behavior with data where domain complexity warrants it; this is not a universal CRUD requirement.

## F04

Edward Hieatt and Rob Mee, in Fowler’s catalog, [Repository](https://martinfowler.com/eaaCatalog/repository.html). A collection-like boundary between domain and data mapping. This does not mandate a Generic Repository in every application.

## F05

Martin Fowler, [Self Testing Code](https://martinfowler.com/bliki/SelfTestingCode.html). Automated tests evolve with code and support safe changes. Self-testing code and TDD are distinct concepts.

## F06

Martin Fowler, [Test Coverage](https://martinfowler.com/bliki/TestCoverage.html). Coverage helps find untested areas; a high number alone does not establish test quality.

## F07

Martin Fowler, [Mocks Aren’t Stubs](https://martinfowler.com/articles/mocksArentStubs.html). Distinguishes test doubles, state/behavior verification, and testing styles. It does not justify a blanket ban on mocks.

## F08

Martin Fowler, [Continuous Integration](https://martinfowler.com/articles/continuousIntegration.html). Frequent integration, automated builds/tests, and rapid feedback. Merely running a service on feature branches does not establish this practice.

## F09

Martin Fowler, [YAGNI](https://martinfowler.com/bliki/Yagni.html). Avoid speculative functionality while retaining investment in tests, refactoring, and changeability.

## A01

Simon Brown, [Modular Monolith](https://simonbrown.je/modular-monolith/). Discusses component encapsulation and enforcing boundaries through available compiler/build mechanisms. Our rule is to enforce selected boundaries where practical, not impose one topology.

## A02

Mark Richards, [Lesson 157: Architecture Decision Records](https://www.developertoarchitect.com/lessons/lesson157.html). The public lesson summary discusses documenting architectural justification and trade-offs. Only that text was inspected; no claim of reviewing the video or books is made.

## A03

Kent Beck; Martin Fowler, [Test Driven Development](https://martinfowler.com/bliki/TestDrivenDevelopment.html). Fowler describes Beck’s test-first feedback cycle. TDD is recommended where useful; the standard requires meaningful tests without claiming every test must be written first. Beck’s own [site](https://kentbeck.com/) provides author context.

## S01

IETF, [RFC 9457: Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457.html). Defines an HTTP error representation. Choosing it as the default for REST JSON APIs is our policy.

## S02

OWASP, [Application Security Verification Standard](https://asvs.owasp.org/). A security requirements/verification framework. Projects select applicable requirements and blocking policy; no full ASVS compliance or certification is claimed.

## S03

OWASP, [API1:2023 Broken Object Level Authorization](https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization/). Object-level authorization must be checked for the requested object; negative access tests address a risk that authentication alone does not resolve.

## P01

Python, [PEP 8](https://peps.python.org/pep-0008/). Readability, naming, and style. Ruff and an 88-character format limit are our defaults, not universal PEP requirements.

## P02

Python, [typing](https://docs.python.org/3/library/typing.html). Annotations do not automatically enforce runtime validation. Validate untrusted input separately.

## P03

PyPA, [Writing your pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/). Project metadata, dependencies, and tool configuration. Choosing uv and a src layout is our default.

## P04

Astral, [Ruff formatter](https://docs.astral.sh/ruff/formatter/). Formatting and check behavior; the [linter](https://docs.astral.sh/ruff/linter/) separately documents rule selection and exit behavior. Explicitly select the lint policy.

## P05

mypy, [Command line](https://mypy.readthedocs.io/en/stable/command_line.html). Strict options depend on the pinned version and do not enable every conceivable analysis.

## P06

pytest, [Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html). Package/import layout and importlib mode. [Exit codes](https://docs.pytest.org/en/stable/reference/exit-codes.html) include the no-tests-collected condition.

## P07

Astral uv, [Locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/). Locked verification and sync behavior. uv is our package-manager choice.

## N01

Microsoft, [.NET Coding Conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions). C# guidance informs project analyzers and style configuration.

## N02

Microsoft, [Nullable reference types](https://learn.microsoft.com/en-us/dotnet/csharp/nullable-references). Nullability analysis. Mandatory enablement is this profile’s policy.

## N03

Microsoft, [ASP.NET Core Best Practices](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/best-practices). Async I/O, blocking calls, HttpClient, and request lifetimes.

## N04

Microsoft, [Dependency injection guidelines](https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection-guidelines). Lifetimes and resource cleanup. This does not require DI for every pure object.

## N05

Microsoft, [Integration tests in ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/testing/integration-testing). WebApplicationFactory and the test host. An in-memory HTTP host and a real database engine are separate decisions.

## N06

Microsoft NuGet, [Locking dependencies](https://learn.microsoft.com/en-us/nuget/consume-packages/package-references-in-project-files#locking-dependencies). Lock files and dotnet restore --locked-mode behavior.

## N07

Microsoft, [dotnet format](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-format). Formatting/analyzer options and verify-no-changes behavior.

## N08

Microsoft, [dotnet test](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test). Options differ between VSTest and Microsoft.Testing.Platform. xUnit with VSTest is our selected draft profile; executed-test counts require an additional gate.

## G01

Go, [Code Review Comments](https://go.dev/wiki/CodeReviewComments). Packages, interfaces, context, and errors. Discusses defining interfaces with consumers rather than solely for mocking.

## G02

Go, [Managing dependencies](https://go.dev/doc/modules/managing-dependencies). Dependency management through modules.

## G03

Go, [Modules Reference](https://go.dev/ref/mod). Tidy diff and readonly behavior. go mod tidy -diff reports differences without modifying files and returns nonzero for a diff.

## G04

Go, [Data Race Detector](https://go.dev/doc/articles/race_detector). Race detection covers executed paths and has platform/toolchain requirements.

## G05

Go standard library, [net/http/httptest](https://pkg.go.dev/net/http/httptest). Tools for testing HTTP handlers and servers.

## G06

Go standard library, [context](https://pkg.go.dev/context). Propagates deadlines and cancellation across API boundaries.

## G07

Go standard library, [testing](https://pkg.go.dev/testing). The Go test framework. Rejecting zero executed tests in required suites is an additional policy of this standard.

## H01

Anthropic, [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents). Engineering guidance on focused context, retrieval, compaction, and durable notes. It does not establish a universal per-task token/cost optimum.

## H02

Anthropic, [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents). Experience with incremental work, progress handoffs, and verification across sessions. Treat this as an engineering report, not a general benchmark.

## H03

Birgitta Böckeler, published on martinfowler.com, [Harness engineering](https://martinfowler.com/articles/harness-engineering.html). Discusses guidance and feedback mechanisms, including limits of generated tests and coverage for functional confidence. Attribute this article to Böckeler, not Fowler.

## H04

Ryan Lopopolo, OpenAI, [Harness engineering](https://openai.com/index/harness-engineering/). A team experience report on agent development, repository knowledge, and feedback. It is not proof that every project should adopt the same automation or autonomy.
