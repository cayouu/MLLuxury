using LuxuryForecast.API.Services;
using Microsoft.AspNetCore.Mvc;

namespace LuxuryForecast.API.Controllers;

[ApiController]
[Route("api/[controller]")]
public class HistoricalDataController : ControllerBase
{
    private readonly SalesDataAggregationService _dataService;
    private readonly ILogger<HistoricalDataController> _logger;

    public HistoricalDataController(
        SalesDataAggregationService dataService,
        ILogger<HistoricalDataController> logger)
    {
        _dataService = dataService;
        _logger = logger;
    }

    [HttpGet("prepare-training-data")]
    public async Task<IActionResult> PrepareTrainingData(
        [FromQuery] DateTime? startDate = null,
        [FromQuery] DateTime? endDate = null)
    {
        try
        {
            var start = startDate ?? DateTime.Now.AddYears(-2);
            var end = endDate ?? DateTime.Now;

            var data = await _dataService.PrepareTrainingDataAsync(start, end);

            return Ok(new
            {
                startDate = start,
                endDate = end,
                recordCount = data.Aggregations.Count,
                data = data.Aggregations
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error preparing training data");
            return StatusCode(500, new { error = "Error preparing training data", details = ex.Message });
        }
    }
}
