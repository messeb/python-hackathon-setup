import { ref } from 'vue'
import { defineStore } from 'pinia'

import { api, ApiError } from '@/api/client'
import type { ChatMessage } from '@/api/types'

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([])
  const streaming = ref(false)
  const error = ref<string | null>(null)
  let controller: AbortController | null = null

  async function send(content: string) {
    const text = content.trim()
    if (!text || streaming.value) return
    error.value = null
    messages.value.push({ role: 'user', content: text })
    const history = messages.value.slice()
    messages.value.push({ role: 'assistant', content: '' })
    // Mutate through the reactive array element so the view updates per token.
    const target = messages.value[messages.value.length - 1]!

    streaming.value = true
    controller = new AbortController()
    try {
      for await (const delta of api.chatStream(history, controller.signal)) {
        target.content += delta
      }
    } catch (e) {
      if (!(e instanceof DOMException && e.name === 'AbortError')) {
        error.value = e instanceof ApiError ? e.message : 'Request failed'
      }
      if (!target.content) messages.value.pop()
    } finally {
      streaming.value = false
      controller = null
    }
  }

  function stop() {
    controller?.abort()
  }

  function reset() {
    stop()
    messages.value = []
    error.value = null
  }

  return { messages, streaming, error, send, stop, reset }
})
