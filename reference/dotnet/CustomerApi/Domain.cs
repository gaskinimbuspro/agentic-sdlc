using System.Text.RegularExpressions;

namespace CustomerApi;

public sealed class InvalidInput : Exception;

public static class Domain
{
    private static readonly Regex Email = new(
        "^[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9-]+(\\.[a-z0-9-]+)+$",
        RegexOptions.CultureInvariant | RegexOptions.NonBacktracking,
        TimeSpan.FromSeconds(1));

    public static (string Name, string Email) Values(string? name, string? email)
    {
        name = name?.Trim() ?? "";
        email = email?.Trim().ToLowerInvariant() ?? "";
        if (name.EnumerateRunes().Count() is < 1 or > 100 || email.Length > 254 || !Email.IsMatch(email))
            throw new InvalidInput();
        return (name, email);
    }
}
