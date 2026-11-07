import { describe, expect, it } from 'vitest'

import { readSse } from '../api/client'

function streamOf(...chunks: string[]): ReadableStream<Uint8Array> {
  const enc = new TextEncoder()
  return new ReadableStream({
    start(controller) {
      chunks.forEach((c) => controller.enqueue(enc.encode(c)))
      controller.close()
    },
  })
}

describe('readSse', () => {
  it('parses events split across chunks', async () => {
    const body = streamOf(
      'event: delta\ndata: {"text":"He',
      'llo"}\n\nevent: done\r\ndata: {}\r\n\r\n',
    )
    const events = []
    for await (const e of readSse(body)) events.push(e)
    expect(events).toEqual([
      { event: 'delta', data: { text: 'Hello' } },
      { event: 'done', data: {} },
    ])
  })
})
