import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

import { useChatStore } from '../stores/chat'

const sse = (body: string) =>
  new Response(body, { headers: { 'Content-Type': 'text/event-stream' } })

describe('chat store', () => {
  beforeEach(() => setActivePinia(createPinia()))

  it('accumulates streamed deltas into the assistant message', async () => {
    vi.stubGlobal(
      'fetch',
      vi
        .fn()
        .mockResolvedValue(
          sse(
            'event: delta\ndata: {"text":"Echo:"}\n\nevent: delta\ndata: {"text":" hi"}\n\nevent: done\ndata: {}\n\n',
          ),
        ),
    )
    const chat = useChatStore()
    await chat.send('hi')
    expect(chat.messages).toEqual([
      { role: 'user', content: 'hi' },
      { role: 'assistant', content: 'Echo: hi' },
    ])
    expect(chat.streaming).toBe(false)
  })

  it('surfaces stream errors', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(sse('event: error\ndata: {"status":429,"detail":"slow down"}\n\n')),
    )
    const chat = useChatStore()
    await chat.send('hi')
    expect(chat.error).toBe('slow down')
    expect(chat.messages).toHaveLength(1)
  })
})
