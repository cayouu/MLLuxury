using LuxuryForecast.API.Models;

namespace LuxuryForecast.API.Services;

public class InventoryOptimizationService
{
    private readonly ILogger<InventoryOptimizationService> _logger;

    public InventoryOptimizationService(ILogger<InventoryOptimizationService> logger)
    {
        _logger = logger;
    }

    public List<ProductionAlert> GenerateAlerts(List<ProductionRecommendation> recommendations)
    {
        var alerts = new List<ProductionAlert>();

        foreach (var rec in recommendations)
        {
            if (rec.RiskOfStockout > 0.8)
            {
                alerts.Add(new ProductionAlert
                {
                    Severity = "High",
                    ProductId = rec.ProductId,
                    Message = $"Risque élevé de rupture de stock (probabilité: {rec.RiskOfStockout:P0})",
                    RecommendedAction = "Augmenter la production immédiatement"
                });
            }

            if (rec.ConfidenceLevel < 0.6)
            {
                alerts.Add(new ProductionAlert
                {
                    Severity = "Medium",
                    ProductId = rec.ProductId,
                    Message = "Prédiction avec incertitude élevée",
                    RecommendedAction = "Monitorer les ventes réelles de près"
                });
            }
        }

        return alerts;
    }

    public decimal CalculateEstimatedRevenue(List<ProductionRecommendation> recommendations, List<Product> products)
    {
        var revenue = 0m;
        var productPriceMap = products.ToDictionary(p => p.Id, p => p.AveragePrice);

        foreach (var rec in recommendations)
        {
            if (productPriceMap.TryGetValue(rec.ProductId, out var price))
            {
                revenue += rec.RecommendedProductionQuantity * price;
            }
        }

        return revenue;
    }
}

