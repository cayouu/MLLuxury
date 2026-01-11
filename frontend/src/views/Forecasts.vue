<template>
  <div class="forecasts">
    <div class="page-header">
      <h2 class="page-title">Prévisions de Demande</h2>
      <div class="page-actions">
        <select v-model="selectedCollection" class="select">
          <option value="Spring2024">Spring 2024</option>
          <option value="Fall2024">Fall 2024</option>
        </select>
        <button @click="loadForecasts" class="btn btn-primary">Actualiser</button>
      </div>
    </div>

    <div v-if="loading" class="loading">Chargement des prévisions...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div v-if="recommendations.length === 0" class="card">
        <p>Aucune prévision disponible.</p>
      </div>

      <div v-for="rec in recommendations" :key="rec.productId" class="card">
        <div class="forecast-header">
          <h3 class="forecast-product">{{ rec.productId }}</h3>
          <div class="forecast-summary">
            <span><strong>Demande totale:</strong> {{ formatNumber(rec.totalPredictedDemand) }} unités</span>
            <span><strong>Production:</strong> {{ formatNumber(rec.recommendedProductionQuantity) }} unités</span>
          </div>
        </div>

        <div class="forecast-stats">
          <div class="stat-item">
            <span class="stat-label">Niveau de confiance</span>
            <span :class="getConfidenceBadge(rec.confidenceLevel)">
              {{ formatPercent(rec.confidenceLevel) }}
            </span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Risque de rupture</span>
            <span :class="getRiskBadge(rec.riskOfStockout)">
              {{ formatPercent(rec.riskOfStockout) }}
            </span>
          </div>
        </div>

        <div class="forecast-chart">
          <h4>Prévisions hebdomadaires (13 semaines)</h4>
          <canvas :id="`chart-${rec.productId}`" ref="chartRefs"></canvas>
        </div>

        <details class="forecast-details">
          <summary>Voir les détails par semaine</summary>
          <table class="table">
            <thead>
              <tr>
                <th>Semaine</th>
                <th>Quantité Prévue</th>
                <th>Intervalle Confiance</th>
                <th>Production Recommandée</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(forecast, idx) in rec.weeklyForecasts" :key="idx">
                <td>Semaine {{ forecast.weekOffset + 1 }}</td>
                <td>{{ formatNumber(forecast.predictedQuantity) }}</td>
                <td>
                  {{ formatNumber(forecast.confidenceLower) }} - {{ formatNumber(forecast.confidenceUpper) }}
                </td>
                <td>{{ formatNumber(forecast.recommendedProduction) }}</td>
              </tr>
            </tbody>
          </table>
        </details>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { forecastApi, type ProductionRecommendation } from '../services/api'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const loading = ref(true)
const error = ref<string | null>(null)
const recommendations = ref<ProductionRecommendation[]>([])
const selectedCollection = ref('Spring2024')
const chartRefs = ref<HTMLCanvasElement[]>([])

onMounted(async () => {
  await loadForecasts()
})

async function loadForecasts() {
  try {
    loading.value = true
    error.value = null
    
    // Produits de test
    const productIds = ['BAG-001', 'BAG-002', 'BAG-003']
    recommendations.value = await forecastApi.getForecast(productIds, 13)
    
    await nextTick()
    renderCharts()
  } catch (err: any) {
    error.value = err.message || 'Erreur lors du chargement des prévisions'
  } finally {
    loading.value = false
  }
}

function renderCharts() {
  recommendations.value.forEach((rec, index) => {
    const canvasId = `chart-${rec.productId}`
    const canvas = document.getElementById(canvasId) as HTMLCanvasElement
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const labels = rec.weeklyForecasts.map(f => `Semaine ${f.weekOffset + 1}`)
    const data = rec.weeklyForecasts.map(f => f.predictedQuantity)
    const upper = rec.weeklyForecasts.map(f => f.confidenceUpper)
    const lower = rec.weeklyForecasts.map(f => f.confidenceLower)

    new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Prédiction',
            data,
            borderColor: '#1a1a1a',
            backgroundColor: 'rgba(26, 26, 26, 0.1)',
            fill: true,
            tension: 0.4
          },
          {
            label: 'Intervalle supérieur',
            data: upper,
            borderColor: '#d4af37',
            borderDash: [5, 5],
            fill: false
          },
          {
            label: 'Intervalle inférieur',
            data: lower,
            borderColor: '#d4af37',
            borderDash: [5, 5],
            fill: false
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'top'
          },
          title: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    })
  })
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat('fr-FR').format(Math.round(value))
}

function formatPercent(value: number): string {
  return new Intl.NumberFormat('fr-FR', {
    style: 'percent',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

function getConfidenceBadge(level: number): string {
  if (level >= 0.8) return 'badge badge-success'
  if (level >= 0.6) return 'badge badge-warning'
  return 'badge badge-error'
}

function getRiskBadge(risk: number): string {
  if (risk >= 0.7) return 'badge badge-error'
  if (risk >= 0.4) return 'badge badge-warning'
  return 'badge badge-success'
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.page-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.select {
  padding: 10px;
  border: 1px solid var(--border);
  border-radius: 4px;
  font-size: 14px;
}

.forecast-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--border);
}

.forecast-product {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary);
}

.forecast-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
  text-align: right;
}

.forecast-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background-color: var(--accent);
  border-radius: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-light);
}

.forecast-chart {
  margin: 24px 0;
}

.forecast-chart h4 {
  margin-bottom: 16px;
  color: var(--text);
}

.forecast-details {
  margin-top: 24px;
}

.forecast-details summary {
  cursor: pointer;
  padding: 12px;
  background-color: var(--accent);
  border-radius: 4px;
  font-weight: 500;
  margin-bottom: 12px;
}

.forecast-details summary:hover {
  background-color: #e8e8e8;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .forecast-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .forecast-summary {
    text-align: left;
    width: 100%;
  }
}
</style>
