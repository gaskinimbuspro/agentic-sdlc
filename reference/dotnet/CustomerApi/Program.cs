using System.Security.Claims;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using CustomerApi;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using Npgsql;

static string Required(string key) => Environment.GetEnvironmentVariable(key) is { Length: > 0 } value
    ? value : throw new InvalidOperationException($"Missing configuration: {key}");
static Task Problem(HttpContext context, int status)
{
    context.Response.StatusCode = status;
    if (status == 401) context.Response.Headers["WWW-Authenticate"] = "Bearer";
    context.Response.ContentType = "application/problem+json";
    return context.Response.WriteAsync(JsonSerializer.Serialize(new { type = "about:blank", title = "Request failed", status }));
}
static Guid Tenant(ClaimsPrincipal user, string scope)
{
    if (!Guid.TryParse(user.FindFirstValue("tenant_id"), out var tenant) ||
        string.IsNullOrEmpty(user.FindFirstValue("sub")) || user.FindFirstValue("scope") is not { } scopes)
        throw new CustomerFailure(401);
    if (!scopes.Split(' ', StringSplitOptions.RemoveEmptyEntries).Contains(scope)) throw new CustomerFailure(403);
    return tenant;
}

var key = Required("JWT_KEY");
if (key.Length < 32) throw new InvalidOperationException("JWT_KEY too short");
var connection = new NpgsqlConnectionStringBuilder
{
    Host = Required("DB_HOST"), Port = int.Parse(Required("DB_PORT")),
    Database = Required("DB_NAME"), Username = Required("DB_USER"), Password = Required("DB_PASSWORD"),
    Timeout = 3, CommandTimeout = 3, IncludeErrorDetail = false, SslMode = SslMode.Disable
};
var builder = WebApplication.CreateBuilder(args);
builder.WebHost.UseUrls("http://127.0.0.1:" + Required("PORT"));
builder.WebHost.ConfigureKestrel(options => options.Limits.MaxRequestBodySize = 8192);
builder.Logging.ClearProviders();
builder.Logging.AddJsonConsole();
builder.Host.UseDefaultServiceProvider(options => { options.ValidateScopes = true; options.ValidateOnBuild = true; });
builder.Services.AddSingleton(_ => NpgsqlDataSource.Create(connection.ConnectionString));
builder.Services.AddSingleton<Store>();
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme).AddJwtBearer(options =>
{
    options.MapInboundClaims = false;
    options.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuerSigningKey = true, IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(key)),
        ValidateIssuer = true, ValidIssuer = "backend-reference", ValidateAudience = true, ValidAudience = "customers",
        ValidateLifetime = true, RequireExpirationTime = true, RequireSignedTokens = true,
        ClockSkew = TimeSpan.Zero, ValidAlgorithms = [SecurityAlgorithms.HmacSha256]
    };
    options.Events = new JwtBearerEvents
    {
        OnChallenge = context => { context.HandleResponse(); return Problem(context.HttpContext, 401); },
        OnForbidden = context => Problem(context.HttpContext, 403)
    };
});
builder.Services.AddAuthorization();
var app = builder.Build();
app.Use(async (context, next) =>
{
    var requestId = Guid.NewGuid().ToString();
    context.Response.Headers["X-Request-ID"] = requestId;
    using var deadline = CancellationTokenSource.CreateLinkedTokenSource(context.RequestAborted);
    deadline.CancelAfter(TimeSpan.FromSeconds(5));
    context.RequestAborted = deadline.Token;
    try { await next(context); }
    catch (InvalidInput) { await Problem(context, 400); }
    catch (DuplicateCustomer) { await Problem(context, 409); }
    catch (CustomerFailure e) { await Problem(context, e.Status); }
    catch (JsonException) { await Problem(context, 400); }
    catch (BadHttpRequestException e) { await Problem(context, e.StatusCode); }
    catch (Exception) { await Problem(context, 503); }
    finally { app.Logger.LogInformation("Request {RequestId} completed {Status}", requestId, context.Response.StatusCode); }
});
app.UseStatusCodePages(status => Problem(status.HttpContext, status.HttpContext.Response.StatusCode));
app.UseAuthentication();
app.UseAuthorization();
app.MapGet("/health/live", () => new { status = "live" });
app.MapGet("/health/ready", async (Store store, CancellationToken ct) =>
{
    await store.Ready(ct);
    return new { status = "ready" };
});
var jsonOptions = new JsonSerializerOptions(JsonSerializerDefaults.Web)
{
    UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow,
    RespectRequiredConstructorParameters = true
};
app.MapPost("/customers", async (HttpContext context, Store store, CancellationToken ct) =>
{
    var tenant = Tenant(context.User, "customers:write");
    var body = await JsonSerializer.DeserializeAsync<CreateRequest>(context.Request.Body, jsonOptions, ct) ?? throw new CustomerFailure(400);
    if (body.TenantId != tenant) throw new CustomerFailure(403);
    var customer = await store.Create(tenant, body.Name ?? "", body.Email ?? "", ct);
    return Results.Json(customer, statusCode: 201);
}).RequireAuthorization();
app.MapGet("/customers", async (HttpContext context, Store store, CancellationToken ct) =>
{
    var tenant = Tenant(context.User, "customers:read");
    var raw = context.Request.Query["limit"].ToString();
    var limit = string.IsNullOrEmpty(raw) ? 20 : int.TryParse(raw, out var parsed) ? parsed : throw new CustomerFailure(400);
    return await store.List(tenant, limit, ct);
}).RequireAuthorization();
app.Run();

public sealed record CreateRequest([property: JsonPropertyName("tenant_id")] Guid TenantId, string? Name, string? Email);
public partial class Program;

public sealed class CustomerFailure(int status) : Exception("Request failed")
{
    public int Status { get; } = status;
}
