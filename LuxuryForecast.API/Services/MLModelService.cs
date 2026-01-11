using LuxuryForecast.API.Models;
using Microsoft.Extensions.Caching.Memory;

namespace LuxuryForecast.API.Services;

public class ForecastMLService
{
    private readonly HttpClient _httpClient;
    private readonly IConfiguration _config;
    private readonly IMemoryCache _cache;
    private readonly ILogger<ForecastMLService> _logger;

    public ForecastMLService(
        HttpClient httpClient,
        IConfiguration config,
        IMemoryCache cache,
        ILogger<ForecastMLService> logger)
    {
        _httpClient = httpClient;
        _config = config;
        _cache = cache;
        _logger = logger;
        _httpClient.BaseAddress = new Uri(config["MLService:BaseUrl"] ?? "http://localhost:8000");
    }

    public async Task<List<ProductionRecommendation>> GetForecastAsync(
        List<string> productIds,
        int horizonWeeks = 13)
    {
        var cacheKey = $"forecast_{string.Join(",", productIds)}_{horizonWeeks}";

        if (_cache.TryGetValue(cacheKey, out List<ProductionRecommendation>? cached) && cached != null)
        {
            _logger.LogInformation("Returning cached forecast for {ProductIds}", string.Join(",", productIds));
            return cached;
        }

        var request = new SalesPredictionRequest
        {
            ProductIds = productIds,
            StartDate = DateTime.Now.ToString("yyyy-MM-dd"),
            ForecastHorizonWeeks = horizonWeeks
        };

        try
        {
            var response = await _httpClient.PostAsJsonAsync("/forecast", request);
            response.EnsureSuccessStatusCode();

            var forecasts = await response.Content.ReadFromJsonAsync<List<ForecastResponse>>()
                ?? new List<ForecastResponse>();

            var recommendations = forecasts
                .GroupBy(f => f.ProductId)
                .Select(g => new ProductionRecommendation
                {
                    ProductId = g.Key,
                    TotalPredictedDemand = g.Sum(f => f.PredictedQuantity),
                    WeeklyForecasts = g.OrderBy(f => f.WeekOffset).ToList(),
                    RecommendedProductionQuantity = CalculateOptimalProduction(g.ToList()),
                    ConfidenceLevel = CalculateConfidence(g.ToList()),
                    RiskOfStockout = AssessStockoutRisk(g.ToList())
                })
                .ToList();

            _cache.Set(cacheKey, recommendations, TimeSpan.FromHours(6));
            return recommendations;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error calling ML service for forecast");
            throw;
        }
    }

    private int CalculateOptimalProduction(List<ForecastResponse> forecasts)
    {
        // Logique métier: production = prédiction + stock sécurité
        var avgDemand = forecasts.Average(f => f.PredictedQuantity);
        var maxDemand = forecasts.Max(f => f.ConfidenceUpper);

        // Pour le luxe: on évite le surstock mais on garantit la disponibilité
        var safetyStock = (maxDemand - avgDemand) * 0.5; // 50% de la variance

        return (int)Math.Ceiling(forecasts.Sum(f => f.PredictedQuantity) + safetyStock);
    }

    private double CalculateConfidence(List<ForecastResponse> forecasts)
    {
        // Calcul de la confiance basée sur l'écart-type des intervalles de confiance
        var avgInterval = forecasts.Average(f => f.ConfidenceUpper - f.ConfidenceLower);
        var avgPrediction = forecasts.Average(f => f.PredictedQuantity);

        if (avgPrediction == 0) return 0;

        // Plus l'intervalle est petit par rapport à la prédiction, plus la confiance est élevée
        var coefficient = avgInterval / avgPrediction;
        return Math.Max(0, Math.Min(1, 1 - coefficient));
    }

    private double AssessStockoutRisk(List<ForecastResponse> forecasts)
    {
        // Calcul du risque de rupture basé sur la probabilité que la demande dépasse le stock disponible
        // Simplification: risque élevé si les prédictions supérieures sont beaucoup plus hautes que la moyenne
        var avgPrediction = forecasts.Average(f => f.PredictedQuantity);
        var maxUpperBound = forecasts.Max(f => f.ConfidenceUpper);

        if (avgPrediction == 0) return 0;

        var riskRatio = (maxUpperBound - avgPrediction) / avgPrediction;
        return Math.Min(1, riskRatio);
    }
}
