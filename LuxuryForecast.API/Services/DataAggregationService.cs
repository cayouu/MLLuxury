using LuxuryForecast.API.Models;

namespace LuxuryForecast.API.Services;

public class SalesDataAggregationService
{
    private readonly ILogger<SalesDataAggregationService> _logger;

    public SalesDataAggregationService(ILogger<SalesDataAggregationService> logger)
    {
        _logger = logger;
    }

    public async Task<HistoricalSalesData> PrepareTrainingDataAsync(
        DateTime startDate,
        DateTime endDate)
    {
        // Note: Dans un vrai projet, ceci utiliserait Entity Framework avec une base de données réelle
        // Pour cet exemple, on simule les données agrégées

        _logger.LogInformation("Preparing training data from {StartDate} to {EndDate}", startDate, endDate);

        // Simulation d'agrégation de données
        // Dans une implémentation réelle, cela ferait appel à _context.Sales avec Entity Framework
        var salesData = new List<SalesAggregation>
        {
            // Exemples de données agrégées
            new SalesAggregation
            {
                ProductId = "BAG-001",
                Collection = "Spring 2024",
                Week = 15,
                Year = 2024,
                Country = "FR",
                Channel = "Boutique",
                QuantitySold = 45,
                Revenue = 225000,
                AveragePrice = 5000
            },
            new SalesAggregation
            {
                ProductId = "BAG-001",
                Collection = "Spring 2024",
                Week = 16,
                Year = 2024,
                Country = "FR",
                Channel = "Online",
                QuantitySold = 23,
                Revenue = 115000,
                AveragePrice = 5000
            }
        };

        return await EnrichWithExternalFactors(salesData);
    }

    private async Task<HistoricalSalesData> EnrichWithExternalFactors(
        List<SalesAggregation> sales)
    {
        // Ajout de features externes
        foreach (var sale in sales)
        {
            sale.IsHolidaySeason = CheckHolidayPeriod(sale.Week, sale.Country);
            sale.FashionWeekProximity = CalculateFashionWeekDistance(sale.Week, sale.Year);
            sale.MarketingCampaignActive = await CheckCampaignActivity(sale.Week, sale.Year);
            sale.EconomicIndex = await GetEconomicIndicator(sale.Country, sale.Year);
        }

        return new HistoricalSalesData { Aggregations = sales };
    }

    private bool CheckHolidayPeriod(int week, string country)
    {
        // Semaines de fêtes (Nov-Dec-Jan)
        return week >= 48 || week <= 4;
    }

    private int CalculateFashionWeekDistance(int week, int year)
    {
        // Fashion Weeks: Février (semaine 7-8) et Septembre (semaine 38-39)
        var fashionWeeks = new[] { 7, 8, 38, 39 };
        var minDistance = fashionWeeks.Min(fw => Math.Abs(week - fw));
        return minDistance;
    }

    private Task<bool> CheckCampaignActivity(int week, int year)
    {
        // Simulation: campagnes actives en début de collection
        return Task.FromResult(week >= 1 && week <= 10);
    }

    private Task<double> GetEconomicIndicator(string country, int year)
    {
        // Simulation d'indicateurs économiques par pays
        var indicators = new Dictionary<string, double>
        {
            { "FR", 1.0 },
            { "US", 1.2 },
            { "CN", 1.5 },
            { "JP", 0.9 },
            { "UK", 0.95 }
        };

        return Task.FromResult(indicators.GetValueOrDefault(country, 1.0));
    }
}
