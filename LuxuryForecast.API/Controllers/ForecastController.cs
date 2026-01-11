using LuxuryForecast.API.Models;
using LuxuryForecast.API.Services;
using Microsoft.AspNetCore.Mvc;

namespace LuxuryForecast.API.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ForecastController : ControllerBase
{
    private readonly ForecastMLService _forecastService;
    private readonly ILogger<ForecastController> _logger;

    public ForecastController(
        ForecastMLService forecastService,
        ILogger<ForecastController> logger)
    {
        _forecastService = forecastService;
        _logger = logger;
    }

    [HttpPost]
    public async Task<ActionResult<List<ProductionRecommendation>>> GetForecast(
        [FromBody] SalesPredictionRequest request)
    {
        try
        {
            var recommendations = await _forecastService.GetForecastAsync(
                request.ProductIds,
                request.ForecastHorizonWeeks
            );

            return Ok(recommendations);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating forecast");
            return StatusCode(500, new { error = "Error generating forecast", details = ex.Message });
        }
    }
}
