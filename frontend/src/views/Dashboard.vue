<template>
  <div class="dashboard">
    <h2 class="page-title">Dashboard</h2>

    <div v-if="loading" class="loading">Chargement...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <!-- Métriques principales -->
      <div class="grid grid-4">
        <div class="metric-card">
          <div class="metric-label">Produits analysés</div>
          <div class="metric-value">{{ report?.totalProductsAnalyzed || 0 }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Unités à produire</div>
          <div class="metric-value">{{ formatNumber(report?.summary.totalUnitsToProduct || 0) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Revenus estimés</div>
          <div class="metric-value">{{ formatCurrency(report?.summary.estimatedRevenue || 0) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Priorité haute</div>
          <div class="metric-value">{{ report?.summary.highPriorityItems || 0 }}</div>
        </div>
      </div>

      <!-- Alertes -->
      <div v-if="report?.alerts && report.alerts.length > 0" class="card">
        <h3 class="card-title">Alertes</h3>
        <div v-for="(alert, index) in report.alerts" :key="index" :class="`alert alert-${alert.severity.toLowerCase()}`">
          <strong>{{ alert.severity }} - {{ alert.productId }}</strong>
          <div>{{ alert.message }}</div>
          <div class="alert-action">{{ alert.recommendedAction }}</div>
        </div>
      </div>

      <!-- Recommandations principales -->
      <div class="card">
        <h3 class="card-title">Recommandations de Production</h3>
        <table class="table">
          <thead>
            <tr>
              <th>Produit</th>
              <th>Demande Prévue</th>
              <th>Production Recommandée</th>
              <th>Confiance</th>
              <th>Risque Rupture</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="rec in topRecommendations" :key="rec.productId">
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
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Informations du rapport -->
      <div class="card">
        <h3 class="card-title">Informations du Rapport</h3>
        <div class="report-info">
          <div><strong>Collection:</strong> {{ report?.collectionId }}</div>
          <div><strong>Horizon:</strong> {{ report?.forecastHorizon }}</div>
          <div><strong>Généré le:</strong> {{ formatDate(report?.generatedAt) }}</div>
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

const topRecommendations = computed(() => {
  if (!report.value) return []
  return report.value.recommendations
    .sort((a, b) => b.riskOfStockout - a.riskOfStockout)
    .slice(0, 10)
})

onMounted(async () => {
  try {
    loading.value = true
    report.value = await forecastApi.getProductionPlan('Spring2024', 13)
  } catch (err: any) {
    error.value = err.message || 'Erreur lors du chargement des données'
  } finally {
    loading.value = false
  }
})

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

function formatDate(dateString?: string): string {
  if (!dateString) return ''
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
.page-title {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 32px;
  color: var(--primary);
}

.report-info {
  display: grid;
  gap: 12px;
}

.report-info > div {
  padding: 8px 0;
  border-bottom: 1px solid var(--border);
}

.report-info > div:last-child {
  border-bottom: none;
}

.alert-action {
  margin-top: 8px;
  font-size: 14px;
  font-style: italic;
}
</style>
