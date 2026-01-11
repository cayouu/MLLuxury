<template>
  <div class="production">
    <div class="page-header">
      <h2 class="page-title">Planification de Production</h2>
      <div class="page-actions">
        <select v-model="selectedCollection" class="select">
          <option value="Spring2024">Spring 2024</option>
          <option value="Fall2024">Fall 2024</option>
        </select>
        <input 
          v-model.number="horizonWeeks" 
          type="number" 
          min="1" 
          max="52" 
          class="input"
          placeholder="Horizon (semaines)"
        />
        <button @click="loadProductionPlan" class="btn btn-primary">Générer Plan</button>
      </div>
    </div>

    <div v-if="loading" class="loading">Génération du plan de production...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="report">
      <!-- Résumé -->
      <div class="grid grid-4">
        <div class="metric-card">
          <div class="metric-label">Produits</div>
          <div class="metric-value">{{ report.totalProductsAnalyzed }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Unités à produire</div>
          <div class="metric-value">{{ formatNumber(report.summary.totalUnitsToProduct) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Revenus estimés</div>
          <div class="metric-value">{{ formatCurrency(report.summary.estimatedRevenue) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Priorités hautes</div>
          <div class="metric-value">{{ report.summary.highPriorityItems }}</div>
        </div>
      </div>

      <!-- Alertes -->
      <div v-if="report.alerts && report.alerts.length > 0" class="card">
        <h3 class="card-title">⚠️ Alertes de Production</h3>
        <div v-for="(alert, index) in report.alerts" :key="index" :class="`alert alert-${alert.severity.toLowerCase()}`">
          <div class="alert-header">
            <strong>{{ alert.severity }} - {{ alert.productId }}</strong>
          </div>
          <div class="alert-message">{{ alert.message }}</div>
          <div class="alert-action">
            <strong>Action recommandée:</strong> {{ alert.recommendedAction }}
          </div>
        </div>
      </div>

      <!-- Recommandations prioritaires -->
      <div class="card">
        <h3 class="card-title">Recommandations par Priorité</h3>
        <table class="table">
          <thead>
            <tr>
              <th>Priorité</th>
              <th>Produit</th>
              <th>Demande Prévue</th>
              <th>Production</th>
              <th>Confiance</th>
              <th>Risque</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="(rec, index) in prioritizedRecommendations" 
              :key="rec.productId"
              :class="{ 'row-high-priority': rec.riskOfStockout > 0.7 }"
            >
              <td>
                <span class="priority-badge">{{ index + 1 }}</span>
              </td>
              <td><strong>{{ rec.productId }}</strong></td>
              <td>{{ formatNumber(rec.totalPredictedDemand) }}</td>
              <td>{{ formatNumber(rec.recommendedProductionQuantity) }}</td>
              <td>
                <span :class="getConfidenceBadge(rec.confidenceLevel)">
                  {{ formatPercent(rec.confidenceLevel) }}
                </span>
              </td>
              <td>
                <span :class="getRiskBadge(rec.riskOfStockout)">
                  {{ formatPercent(rec.riskOfStockout) }}
                </span>
              </td>
              <td>
                <button 
                  v-if="rec.riskOfStockout > 0.7" 
                  class="btn btn-secondary"
                  style="font-size: 12px; padding: 6px 12px;"
                >
                  Urgent
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Détails du rapport -->
      <div class="card">
        <h3 class="card-title">Détails du Plan</h3>
        <div class="plan-details">
          <div class="detail-item">
            <span class="detail-label">Collection:</span>
            <span class="detail-value">{{ report.collectionId }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Horizon de prévision:</span>
            <span class="detail-value">{{ report.forecastHorizon }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Généré le:</span>
            <span class="detail-value">{{ formatDate(report.generatedAt) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { forecastApi, type ProductionPlanReport } from '../services/api'

const loading = ref(true)
const error = ref<string | null>(null)
const report = ref<ProductionPlanReport | null>(null)
const selectedCollection = ref('Spring2024')
const horizonWeeks = ref(13)

const prioritizedRecommendations = computed(() => {
  if (!report.value) return []
  return report.value.recommendations
    .sort((a, b) => {
      // Trier par risque décroissant, puis par confiance croissante
      if (Math.abs(b.riskOfStockout - a.riskOfStockout) > 0.1) {
        return b.riskOfStockout - a.riskOfStockout
      }
      return a.confidenceLevel - b.confidenceLevel
    })
})

onMounted(async () => {
  await loadProductionPlan()
})

async function loadProductionPlan() {
  try {
    loading.value = true
    error.value = null
    report.value = await forecastApi.getProductionPlan(selectedCollection.value, horizonWeeks.value)
  } catch (err: any) {
    error.value = err.message || 'Erreur lors de la génération du plan de production'
  } finally {
    loading.value = false
  }
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat('fr-FR').format(Math.round(value))
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0
  }).format(value)
}

function formatPercent(value: number): string {
  return new Intl.NumberFormat('fr-FR', {
    style: 'percent',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
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
  flex-wrap: wrap;
  gap: 16px;
}

.page-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.select,
.input {
  padding: 10px;
  border: 1px solid var(--border);
  border-radius: 4px;
  font-size: 14px;
}

.input {
  width: 120px;
}

.alert-header {
  margin-bottom: 8px;
}

.alert-message {
  margin-bottom: 8px;
}

.alert-action {
  font-size: 14px;
}

.row-high-priority {
  background-color: #fff5f5 !important;
}

.priority-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--primary);
  color: white;
  font-weight: 700;
}

.plan-details {
  display: grid;
  gap: 16px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 12px;
  background-color: var(--accent);
  border-radius: 4px;
}

.detail-label {
  font-weight: 600;
  color: var(--text-light);
}

.detail-value {
  color: var(--text);
  font-weight: 500;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .detail-item {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
