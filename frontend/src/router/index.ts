import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Forecasts from '../views/Forecasts.vue'
import Production from '../views/Production.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Dashboard',
      component: Dashboard
    },
    {
      path: '/forecasts',
      name: 'Forecasts',
      component: Forecasts
    },
    {
      path: '/production',
      name: 'Production',
      component: Production
    }
  ]
})

export default router
