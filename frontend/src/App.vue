<template>
  <div id="app">
    <nav class="navbar">
      <div class="container">
        <div class="navbar-content">
          <div class="navbar-brand">
            <h1>💼 Luxury Forecast</h1>
            <span class="navbar-subtitle">Prévision de Demande</span>
          </div>
          <div class="navbar-menu">
            <router-link to="/" class="nav-link">Dashboard</router-link>
            <router-link to="/forecasts" class="nav-link">Prévisions</router-link>
            <router-link to="/production" class="nav-link">Planification</router-link>
          </div>
        </div>
      </div>
    </nav>

    <main class="main-content">
      <div class="container">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
// App component
</script>

<style scoped>
.navbar {
  background-color: var(--primary);
  color: white;
  padding: 20px 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.navbar-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navbar-brand h1 {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 4px;
}

.navbar-subtitle {
  font-size: 12px;
  opacity: 0.8;
}

.navbar-menu {
  display: flex;
  gap: 32px;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-weight: 500;
  padding: 8px 0;
  border-bottom: 2px solid transparent;
  transition: border-color 0.2s;
}

.nav-link:hover,
.nav-link.router-link-active {
  border-bottom-color: var(--secondary);
}

.main-content {
  padding: 40px 0;
  min-height: calc(100vh - 100px);
}

@media (max-width: 768px) {
  .navbar-content {
    flex-direction: column;
    gap: 20px;
  }

  .navbar-menu {
    gap: 20px;
  }
}
</style>
