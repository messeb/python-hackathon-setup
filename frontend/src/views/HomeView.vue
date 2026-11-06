<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { api } from '@/api/client'
import type { Health } from '@/api/types'

const health = ref<Health | null>(null)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    health.value = await api.health()
  } catch {
    error.value = 'Backend not reachable. Start it with `make dev-backend`.'
  }
})
</script>

<template>
  <section class="stack">
    <h1>Status</h1>
    <p class="muted">FastAPI backend with LLM, PyTorch and REST endpoints.</p>
    <div class="card">
      <p v-if="error" class="error" role="alert">{{ error }}</p>
      <dl v-else-if="health" class="grid">
        <dt>Status</dt>
        <dd data-testid="status">{{ health.status }}</dd>
        <dt>Version</dt>
        <dd>{{ health.version }}</dd>
        <dt>Environment</dt>
        <dd>{{ health.environment }}</dd>
        <dt>LLM provider</dt>
        <dd>{{ health.llm_provider }}</dd>
        <dt>Torch device</dt>
        <dd>{{ health.torch_device }}</dd>
      </dl>
      <p v-else class="muted">Loading…</p>
    </div>
    <p><a href="/api/docs">OpenAPI docs →</a></p>
  </section>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 0.5rem 1.5rem;
  margin: 0;
}

dt {
  color: var(--muted);
}

dd {
  margin: 0;
  font-weight: 600;
}

a {
  color: var(--accent);
}
</style>
