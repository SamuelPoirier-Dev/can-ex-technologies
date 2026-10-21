import type { Game, GameEvent } from '../api/types'
import { playerName } from './players'

/** One French log line per game event. */
export function describeEvent(event: GameEvent, game: Game): string {
  const name = (id: string) => playerName(game, id)
  const square = (index: number) => game.board[index]?.name ?? `case ${index}`

  switch (event.type) {
    case 'moved':
      return `${name(event.player_id)} lance ${event.roll} et arrive sur ${square(event.to_position)}`
    case 'salary_collected':
      return `${name(event.player_id)} passe par le départ et reçoit ${event.amount} $`
    case 'property_bought':
      return `${name(event.player_id)} achète ${square(event.position)} pour ${event.price} $`
    case 'rent_paid':
      return `${name(event.payer_id)} paie ${event.amount} $ de loyer à ${name(event.owner_id)}`
    case 'bankrupted':
      return `${name(event.player_id)} fait faillite`
    case 'game_won':
      return `${name(event.player_id)} gagne la partie !`
  }
}

/** The most recent dice roll, if any. */
export function lastRoll(game: Game): number | null {
  for (let i = game.events.length - 1; i >= 0; i--) {
    const event = game.events[i]
    if (event.type === 'moved') return event.roll
  }
  return null
}
