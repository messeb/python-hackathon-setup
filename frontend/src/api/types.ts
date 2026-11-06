// Mirrors backend/src/app/schemas. Regenerate from /api/openapi.json if it grows.

export interface Health {
  status: string
  version: string
  environment: string
  llm_provider: string
  torch_device: string
}

export type Role = 'user' | 'assistant'

export interface ChatMessage {
  role: Role
  content: string
}

export interface ProviderInfo {
  provider: string
  model: string
}

export interface TorchInfo {
  torch_version: string
  device: string
  cuda_available: boolean
  mps_available: boolean
  threads: number
}

export interface RegressionResult {
  slope: number
  intercept: number
  final_loss: number
  epochs: number
}

export interface Item {
  id: string
  name: string
  description: string | null
  price: number
  created_at: string
}

export type ItemCreate = Pick<Item, 'name' | 'price'> & { description?: string | null }
