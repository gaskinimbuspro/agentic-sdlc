using System.Text.Json.Serialization;
using Npgsql;

namespace CustomerApi;

public sealed record Customer(
    Guid Id,
    [property: JsonPropertyName("tenant_id")] Guid TenantId,
    string Name,
    string Email);

public sealed class Store(NpgsqlDataSource source)
{
    public async Task<Customer> Create(Guid tenant, string name, string email, CancellationToken ct)
    {
        var values = Domain.Values(name, email);
        var id = Guid.NewGuid();
        await using var connection = await source.OpenConnectionAsync(ct);
        await using var transaction = await connection.BeginTransactionAsync(ct);
        try
        {
            await using var insert = new NpgsqlCommand("INSERT INTO customers VALUES ($1,$2,$3,$4)", connection, transaction);
            insert.Parameters.Add(new NpgsqlParameter { Value = id });
            insert.Parameters.Add(new NpgsqlParameter { Value = tenant });
            insert.Parameters.Add(new NpgsqlParameter { Value = values.Name });
            insert.Parameters.Add(new NpgsqlParameter { Value = values.Email });
            await insert.ExecuteNonQueryAsync(ct);
            await using var audit = new NpgsqlCommand("INSERT INTO customer_audit(customer_id) VALUES ($1)", connection, transaction);
            audit.Parameters.Add(new NpgsqlParameter { Value = id });
            await audit.ExecuteNonQueryAsync(ct);
            await transaction.CommitAsync(ct);
        }
        catch (PostgresException e) when (e.SqlState == "23505")
        {
            throw new CustomerFailure(409);
        }
        return new Customer(id, tenant, values.Name, values.Email);
    }

    public async Task<List<Customer>> List(Guid tenant, int limit, CancellationToken ct)
    {
        if (limit is < 1 or > 100) throw new CustomerFailure(400);
        await using var command = source.CreateCommand("SELECT id,tenant_id,name,email FROM customers WHERE tenant_id=$1 ORDER BY id LIMIT $2");
        command.Parameters.Add(new NpgsqlParameter { Value = tenant });
        command.Parameters.Add(new NpgsqlParameter { Value = limit });
        await using var reader = await command.ExecuteReaderAsync(ct);
        List<Customer> result = [];
        while (await reader.ReadAsync(ct))
            result.Add(new Customer(reader.GetGuid(0), reader.GetGuid(1), reader.GetString(2), reader.GetString(3)));
        return result;
    }
}
