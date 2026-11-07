<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'

const links = [
  { to: '/', label: 'Status' },
  { to: '/chat', label: 'LLM Chat' },
  { to: '/ml', label: 'PyTorch' },
  { to: '/items', label: 'Items' },
]
</script>

<template>
  <header class="header">
    <strong class="brand">Hackathon Starter</strong>
    <nav class="row" aria-label="Main">
      <RouterLink v-for="link in links" :key="link.to" :to="link.to">{{ link.label }}</RouterLink>
    </nav>
  </header>
  <main class="main">
    <RouterView />
  </main>
</template>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding: 1rem;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
}

.header a {
  color: var(--muted);
  text-decoration: none;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
}

.header a.router-link-exact-active {
  color: var(--text);
  background: var(--bg);
}

.main {
  max-width: 860px;
  margin: 0 auto;
  padding: 1.5rem 1rem 4rem;
}
</style>
