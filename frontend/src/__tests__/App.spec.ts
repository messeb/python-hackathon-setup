import { afterEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia } from 'pinia'

import App from '../App.vue'
import router from '../router'

describe('App', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('renders navigation and backend status', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            status: 'ok',
            version: '0.1.0',
            environment: 'test',
            llm_provider: 'fake',
            torch_device: 'cpu',
          }),
        ),
      ),
    )
    await router.push('/')
    const wrapper = mount(App, { global: { plugins: [createPinia(), router] } })
    await flushPromises()

    expect(wrapper.text()).toContain('LLM Chat')
    expect(wrapper.get('[data-testid="status"]').text()).toBe('ok')
  })
})
