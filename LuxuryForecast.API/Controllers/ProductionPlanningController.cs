using LuxuryForecast.API.Models;
using LuxuryForecast.API.Services;
using Microsoft.AspNetCore.Mvc;

namespace LuxuryForecast.API.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ProductionPlanningController : ControllerBase
{
    private readonly ForecastMLService _forecastService;
    private readonly InventoryOptimizationService _optimizationService;
    private readonly IProductService _productService;
    private readonly ILogger<ProductionPlanningController> _logger;

    public ProductionPlanningController(
        ForecastMLService forecastService,
        InventoryOptimizationService optimizationService,
        IProductService productService,
        ILogger<ProductionPlanningController> logger)
    {
        _forecastService = forecastService;
        _optimizationService = optimizationService;
        _productService = productService;
        _logger = logger;
    }

    [HttpGet("recommendations/{collectionId}")]
    public async Task<ActionResult<ProductionPlanReport>> GetProductionPlan(
        string collectionId,
        [FromQuery] int horizonWeeks = 13)
    {
        try
        {
            // Récupération des produits de la collection
            var products = await _productService.GetByCollectionAsync(collectionId);

            // Appel au service ML
            var forecasts = await _forecastService.GetForecastAsync(
                products.Select(p => p.Id).ToList(),
                horizonWeeks
            );

            // Priorisation basée sur plusieurs critères
            var prioritizedProducts = forecasts
                .OrderByDescending(f => f.RiskOfStockout)      // Risque de rupture
                .ThenByDescending(f => f.TotalPredictedDemand) // Demande totale
                .ThenBy(f => f.ConfidenceLevel)                // Certitude basse = priorité
                .ToList();

            var report = new ProductionPlanReport
            {
                CollectionId = collectionId,
                GeneratedAt = DateTime.UtcNow,
                ForecastHorizon = $"{horizonWeeks} weeks",
                TotalProductsAnalyzed = products.Count,
                Recommendations = prioritizedProducts,
                Alerts = _optimizationService.GenerateAlerts(prioritizedProducts),
                Summary = new ProductionSummary
                {
                    TotalUnitsToProduct = prioritizedProducts.Sum(p => p.RecommendedProductionQuantity),
                    HighPriorityItems = prioritizedProducts.Count(p => p.RiskOfStockout > 0.7),
                    EstimatedRevenue = _optimizationService.CalculateEstimatedRevenue(prioritizedProducts, products)
                }
            };

            return Ok(report);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating production plan for collection {CollectionId}", collectionId);
            return StatusCode(500, new { error = "Error generating production plan", details = ex.Message });
        }
    }
}
