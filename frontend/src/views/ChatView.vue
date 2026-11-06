<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'

import { api } from '@/api/client'
import type { ProviderInfo } from '@/api/types'
import { useChatStore } from '@/stores/chat'

const chat = useChatStore()
const { messages, streaming, error } = storeToRefs(chat)
const draft = ref('')
const info = ref<ProviderInfo | null>(null)

onMounted(async () => {
  info.value = await api.llmInfo().catch(() => null)
})

function submit() {
  const text = draft.value
  draft.value = ''
  void chat.send(text)
}
</script>

<template>
  <section class="stack">
    <h1>LLM Chat</h1>
    <p class="muted">
      Streams tokens over Server-Sent Events from <code>POST /api/v1/llm/chat/stream</code>.
      <template v-if="info">
        Provider: <strong>{{ info.provider }}</strong> · {{ info.model }}</template
      >
    </p>

    <div class="card log" aria-live="polite">
      <p v-if="!messages.length" class="muted">Say hello to start.</p>
      <div v-for="(m, i) in messages" :key="i" :class="['msg', m.role]">
        <span class="who">{{ m.role === 'user' ? 'You' : 'Assistant' }}</span>
        <p>{{ m.content || '…' }}</p>
      </div>
    </div>
    <p v-if="error" class="error" role="alert">{{ error }}</p>

    <form class="row" @submit.prevent="submit">
      <label class="sr-only" for="prompt">Message</label>
      <input
        id="prompt"
        v-model="draft"
        class="grow"
        placeholder="Ask something…"
        autocomplete="off"
      />
      <button v-if="!streaming" type="submit" :disabled="!draft.trim()">Send</button>
      <button v-else type="button" class="secondary" @click="chat.stop()">Stop</button>
      <button type="button" class="secondary" @click="chat.reset()">Clear</button>
    </form>
  </section>
</template>

<style scoped>
.log {
  min-height: 12rem;
  max-height: 60vh;
  overflow-y: auto;
}

.msg + .msg {
  margin-top: 0.75rem;
}

.msg p {
  margin: 0.125rem 0 0;
  white-space: pre-wrap;
}

.who {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--muted);
}

.msg.assistant .who {
  color: var(--accent);
}

.grow {
  flex: 1;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip-path: inset(50%);
}
</style>
