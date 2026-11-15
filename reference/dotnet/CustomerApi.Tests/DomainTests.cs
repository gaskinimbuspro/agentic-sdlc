using CustomerApi;
using Xunit;

public sealed class DomainTests
{
    [Fact]
    public void Normalization()
    {
        Assert.Equal(("Ada", "ada@example.test"), Domain.Values(" Ada ", " ADA@EXAMPLE.TEST "));
    }

    [Theory]
    [InlineData("", "a@b.test")]
    [InlineData("Ada", "invalid")]
    [InlineData("Ada", "a@b")]
    public void RejectsInvalidValues(string name, string email)
    {
        Assert.Throws<InvalidInput>(() => Domain.Values(name, email));
    }
}
