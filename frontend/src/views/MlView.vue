<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { api, ApiError } from '@/api/client'
import type { RegressionResult, TorchInfo } from '@/api/types'

const info = ref<TorchInfo | null>(null)
const vectors = ref('1, 0, 0\n0.9, 0.1, 0\n0, 1, 0')
const matrix = ref<number[][] | null>(null)
const points = ref('1, 3.1\n2, 4.9\n3, 7.2\n4, 8.8\n5, 11.1')
const fit = ref<RegressionResult | null>(null)
const error = ref<string | null>(null)

const parse = (text: string) =>
  text
    .trim()
    .split('\n')
    .map((line) => line.split(',').map((n) => Number(n.trim())))

async function run<T>(fn: () => Promise<T>): Promise<T | null> {
  error.value = null
  try {
    return await fn()
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Request failed'
    return null
  }
}

async function computeSimilarity() {
  matrix.value = (await run(() => api.similarity(parse(vectors.value))))?.matrix ?? null
}

async function computeRegression() {
  const rows = parse(points.value)
  fit.value = await run(() =>
    api.regression(
      rows.map((r) => r[0] ?? 0),
      rows.map((r) => r[1] ?? 0),
    ),
  )
}

onMounted(async () => {
  info.value = await api.torchInfo().catch(() => null)
})
</script>

<template>
  <section class="stack">
    <h1>PyTorch</h1>
    <p v-if="info" class="muted">
      torch {{ info.torch_version }} on <strong>{{ info.device }}</strong> ·
      {{ info.threads }} threads
    </p>
    <p v-if="error" class="error" role="alert">{{ error }}</p>

    <div class="card stack">
      <h2>Cosine similarity</h2>
      <label for="vectors" class="muted">One vector per line, comma separated</label>
      <textarea id="vectors" v-model="vectors" rows="4" />
      <button type="button" @click="computeSimilarity">Compute</button>
      <table v-if="matrix">
        <tr v-for="(row, i) in matrix" :key="i">
          <td v-for="(v, j) in row" :key="j">{{ v.toFixed(3) }}</td>
        </tr>
      </table>
    </div>

    <div class="card stack">
      <h2>Linear regression (autograd)</h2>
      <label for="points" class="muted">x, y per line</label>
      <textarea id="points" v-model="points" rows="5" />
      <button type="button" @click="computeRegression">Fit</button>
      <p v-if="fit">
        y = <strong>{{ fit.slope.toFixed(3) }}</strong
        >·x +
        <strong>{{ fit.intercept.toFixed(3) }}</strong>
        <span class="muted"> (MSE {{ fit.final_loss.toFixed(4) }})</span>
      </p>
    </div>
  </section>
</template>

<style scoped>
textarea {
  width: 100%;
  font-family: ui-monospace, monospace;
}

table {
  border-collapse: collapse;
  font-variant-numeric: tabular-nums;
}

td {
  border: 1px solid var(--border);
  padding: 0.25rem 0.75rem;
  text-align: right;
}
</style>
