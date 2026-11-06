<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { api, ApiError } from '@/api/client'
import type { Item } from '@/api/types'

const items = ref<Item[]>([])
const name = ref('')
const price = ref<number>(0)
const error = ref<string | null>(null)

async function load() {
  items.value = await api.listItems()
}

async function add() {
  error.value = null
  try {
    await api.createItem({ name: name.value, price: price.value })
    name.value = ''
    price.value = 0
    await load()
  } catch (e) {
    error.value = e instanceof ApiError ? `Invalid item (${e.status})` : 'Request failed'
  }
}

async function remove(id: string) {
  await api.deleteItem(id)
  await load()
}

onMounted(() => load().catch(() => (error.value = 'Backend not reachable')))
</script>

<template>
  <section class="stack">
    <h1>Items</h1>
    <p class="muted">Plain REST CRUD on <code>/api/v1/items</code> (in-memory repository).</p>
    <form class="row card" @submit.prevent="add">
      <input v-model="name" placeholder="Name" aria-label="Name" required />
      <input v-model.number="price" type="number" min="0" step="0.01" aria-label="Price" />
      <button type="submit" :disabled="!name">Add</button>
    </form>
    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <ul class="list">
      <li v-for="item in items" :key="item.id" class="card row">
        <span class="grow">{{ item.name }}</span>
        <span class="muted">{{ item.price.toFixed(2) }}</span>
        <button type="button" class="secondary" @click="remove(item.id)">Delete</button>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.list {
  list-style: none;
  padding: 0;
  display: grid;
  gap: 0.5rem;
}

.grow {
  flex: 1;
}
</style>
