// Hand-written mirror of the backend schemas (backend/app/api/schemas.py).

export type GameStatus = 'waiting' | 'in_progress' | 'finished'

export type Square = {
  index: number
  name: string
  price: number | null
  rent: number | null
  owner_id: string | null
}

export type Player = {
  id: string
  name: string
  money: number
  position: number
  is_bankrupt: boolean
  properties: number[]
}

export type GameEvent =
  | { type: 'moved'; player_id: string; roll: number; from_position: number; to_position: number }
  | { type: 'salary_collected'; player_id: string; amount: number }
  | { type: 'property_bought'; player_id: string; position: number; price: number }
  | { type: 'rent_paid'; payer_id: string; owner_id: string; position: number; amount: number }
  | { type: 'bankrupted'; player_id: string; creditor_id: string }
  | { type: 'game_won'; player_id: string }

export type Game = {
  id: string
  status: GameStatus
  max_players: number
  players: Player[]
  board: Square[]
  current_player_id: string | null
  winner_id: string | null
  events: GameEvent[]
}

export type JoinResponse = {
  player_id: string
  token: string
  game: Game
}

export type LiveMessage = { type: 'state'; game: Game }
