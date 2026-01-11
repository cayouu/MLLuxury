using LuxuryForecast.API.Models;

namespace LuxuryForecast.API.Services;

public interface IProductService
{
    Task<List<Product>> GetByCollectionAsync(string collectionId);
}

public class ProductService : IProductService
{
    private readonly ILogger<ProductService> _logger;

    public ProductService(ILogger<ProductService> logger)
    {
        _logger = logger;
    }

    public Task<List<Product>> GetByCollectionAsync(string collectionId)
    {
        // Simulation: Dans un vrai projet, ceci ferait appel à la base de données
        var products = new List<Product>
        {
            new Product { Id = "BAG-001", Name = "Sac Iconique", Collection = collectionId, AveragePrice = 5000 },
            new Product { Id = "BAG-002", Name = "Malle Voyage", Collection = collectionId, AveragePrice = 12000 },
            new Product { Id = "BAG-003", Name = "Petit Sac", Collection = collectionId, AveragePrice = 3500 }
        };

        return Task.FromResult(products);
    }
}
