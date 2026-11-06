import type {
  ChatMessage,
  Health,
  Item,
  ItemCreate,
  ProviderInfo,
  RegressionResult,
  TorchInfo,
} from './types'

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(path, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init.headers },
  })
  if (!res.ok) {
    const body = (await res.json().catch(() => ({}))) as { detail?: unknown }
    const detail = typeof body.detail === 'string' ? body.detail : res.statusText
    throw new ApiError(res.status, detail)
  }
  return (res.status === 204 ? undefined : await res.json()) as T
}

const json = (body: unknown): RequestInit => ({ method: 'POST', body: JSON.stringify(body) })

export interface SseEvent {
  event: string
  data: unknown
}

/** Parse a `text/event-stream` body into events (works for POST, unlike EventSource). */
export async function* readSse(body: ReadableStream<Uint8Array>): AsyncGenerator<SseEvent> {
  const reader = body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  for (;;) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true }).replace(/\r\n/g, '\n')
    let sep: number
    while ((sep = buffer.indexOf('\n\n')) !== -1) {
      const block = buffer.slice(0, sep)
      buffer = buffer.slice(sep + 2)
      let event = 'message'
      const data: string[] = []
      for (const line of block.split('\n')) {
        if (line.startsWith('event:')) event = line.slice(6).trim()
        else if (line.startsWith('data:')) data.push(line.slice(5).trimStart())
      }
      if (data.length) yield { event, data: JSON.parse(data.join('\n')) }
    }
  }
}

export const api = {
  health: () => request<Health>('/health/ready'),

  llmInfo: () => request<ProviderInfo>('/api/v1/llm/info'),
  async *chatStream(messages: ChatMessage[], signal?: AbortSignal): AsyncGenerator<string> {
    const res = await fetch('/api/v1/llm/chat/stream', {
      ...json({ messages }),
      headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
      signal,
    })
    if (!res.ok || !res.body) throw new ApiError(res.status, res.statusText)
    for await (const { event, data } of readSse(res.body)) {
      if (event === 'delta') yield (data as { text: string }).text
      else if (event === 'error') {
        const err = data as { status: number; detail: string }
        throw new ApiError(err.status, err.detail)
      }
    }
  },

  torchInfo: () => request<TorchInfo>('/api/v1/ml/info'),
  similarity: (vectors: number[][]) =>
    request<{ matrix: number[][] }>('/api/v1/ml/similarity', json({ vectors })),
  regression: (x: number[], y: number[]) =>
    request<RegressionResult>('/api/v1/ml/regression', json({ x, y, epochs: 1000 })),

  listItems: () => request<Item[]>('/api/v1/items'),
  createItem: (item: ItemCreate) => request<Item>('/api/v1/items', json(item)),
  deleteItem: (id: string) => request<void>(`/api/v1/items/${id}`, { method: 'DELETE' }),
}
