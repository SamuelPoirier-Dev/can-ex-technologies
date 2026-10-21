import type { JoinResponse } from './types'

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init.headers },
  })
  const body = await response.json().catch(() => null)
  if (!response.ok) {
    throw new ApiError(response.status, errorMessage(response.status, body))
  }
  return body as T
}

function errorMessage(status: number, body: unknown): string {
  const detail = (body as { detail?: unknown } | null)?.detail
  // FastAPI returns a string for our errors, a list for validation errors (422).
  if (typeof detail === 'string') return detail
  if (status === 422) return 'Entrée invalide'
  return `Erreur ${status}`
}

export function createGame(playerName: string, maxPlayers: number): Promise<JoinResponse> {
  return request('/api/games', {
    method: 'POST',
    body: JSON.stringify({ player_name: playerName, max_players: maxPlayers }),
  })
}

export function joinGame(code: string, playerName: string): Promise<JoinResponse> {
  return request(`/api/games/${code}/players`, {
    method: 'POST',
    body: JSON.stringify({ player_name: playerName }),
  })
}

// The resulting state arrives through the WebSocket; the response only matters for errors.
export async function playTurn(code: string, token: string): Promise<void> {
  await request(`/api/games/${code}/turns`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  })
}
