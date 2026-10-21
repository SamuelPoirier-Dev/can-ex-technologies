import type { Game } from '../api/types'

const PLAYER_COLORS = ['#d9480f', '#1971c2', '#2f9e44', '#9c36b5']

/** Stable color per player, based on join order. */
export function playerColor(game: Game, playerId: string): string {
  const index = game.players.findIndex((p) => p.id === playerId)
  return PLAYER_COLORS[index % PLAYER_COLORS.length] ?? '#868e96'
}

export function playerName(game: Game, playerId: string): string {
  return game.players.find((p) => p.id === playerId)?.name ?? playerId
}
