namespace LuxuryForecast.API.Models;

public class SalesPredictionRequest
{
    public List<string> ProductIds { get; set; } = new();
    public string StartDate { get; set; } = string.Empty;
    public int ForecastHorizonWeeks { get; set; } = 13;
    public string Channel { get; set; } = "All";
    public List<string> Countries { get; set; } = new() { "All" };
}

public class ForecastResponse
{
    public string ProductId { get; set; } = string.Empty;
    public int WeekOffset { get; set; }
    public double PredictedQuantity { get; set; }
    public double ConfidenceLower { get; set; }
    public double ConfidenceUpper { get; set; }
    public int RecommendedProduction { get; set; }
}

public class ProductionRecommendation
{
    public string ProductId { get; set; } = string.Empty;
    public double TotalPredictedDemand { get; set; }
    public List<ForecastResponse> WeeklyForecasts { get; set; } = new();
    public int RecommendedProductionQuantity { get; set; }
    public double ConfidenceLevel { get; set; }
    public double RiskOfStockout { get; set; }
}

public class ProductionPlanReport
{
    public string CollectionId { get; set; } = string.Empty;
    public DateTime GeneratedAt { get; set; }
    public string ForecastHorizon { get; set; } = string.Empty;
    public int TotalProductsAnalyzed { get; set; }
    public List<ProductionRecommendation> Recommendations { get; set; } = new();
    public List<ProductionAlert> Alerts { get; set; } = new();
    public ProductionSummary Summary { get; set; } = new();
}

public class ProductionAlert
{
    public string Severity { get; set; } = string.Empty;
    public string ProductId { get; set; } = string.Empty;
    public string Message { get; set; } = string.Empty;
    public string RecommendedAction { get; set; } = string.Empty;
}

public class ProductionSummary
{
    public int TotalUnitsToProduct { get; set; }
    public int HighPriorityItems { get; set; }
    public decimal EstimatedRevenue { get; set; }
}

public class SalesAggregation
{
    public string ProductId { get; set; } = string.Empty;
    public string Collection { get; set; } = string.Empty;
    public int Week { get; set; }
    public int Year { get; set; }
    public string Country { get; set; } = string.Empty;
    public string Channel { get; set; } = string.Empty;
    public int QuantitySold { get; set; }
    public decimal Revenue { get; set; }
    public decimal AveragePrice { get; set; }
    public bool IsHolidaySeason { get; set; }
    public int FashionWeekProximity { get; set; }
    public bool MarketingCampaignActive { get; set; }
    public double EconomicIndex { get; set; }
}

public class HistoricalSalesData
{
    public List<SalesAggregation> Aggregations { get; set; } = new();
}

public class Product
{
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string Collection { get; set; } = string.Empty;
    public decimal AveragePrice { get; set; }
}
