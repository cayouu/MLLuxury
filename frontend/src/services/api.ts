import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export interface ForecastResponse {
  productId: string
  weekOffset: number
  predictedQuantity: number
  confidenceLower: number
  confidenceUpper: number
  recommendedProduction: number
}

export interface ProductionRecommendation {
  productId: string
  totalPredictedDemand: number
  weeklyForecasts: ForecastResponse[]
  recommendedProductionQuantity: number
  confidenceLevel: number
  riskOfStockout: number
}

export interface ProductionAlert {
  severity: string
  productId: string
  message: string
  recommendedAction: string
}

export interface ProductionPlanReport {
  collectionId: string
  generatedAt: string
  forecastHorizon: string
  totalProductsAnalyzed: number
  recommendations: ProductionRecommendation[]
  alerts: ProductionAlert[]
  summary: {
    totalUnitsToProduct: number
    highPriorityItems: number
    estimatedRevenue: number
  }
}

export const forecastApi = {
  async getForecast(productIds: string[], horizonWeeks: number = 13): Promise<ProductionRecommendation[]> {
    const response = await api.post<ProductionRecommendation[]>('/Forecast', {
      productIds,
      startDate: new Date().toISOString().split('T')[0],
      forecastHorizonWeeks: horizonWeeks
    })
    return response.data
  },

  async getProductionPlan(collectionId: string, horizonWeeks: number = 13): Promise<ProductionPlanReport> {
    const response = await api.get<ProductionPlanReport>(
      `/ProductionPlanning/recommendations/${collectionId}?horizonWeeks=${horizonWeeks}`
    )
    return response.data
  }
}

export default api
