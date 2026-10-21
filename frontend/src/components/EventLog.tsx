import type { Game } from '../api/types'
import { describeEvent } from '../lib/events'

type Props = { game: Game }

function EventLog({ game }: Props) {
  // Newest first. Events are append-only, so the index is a stable key.
  const entries = game.events.map((event, index) => ({ event, index })).reverse()

  return (
    <section className="card">
      <h2>Journal</h2>
      {entries.length === 0 ? (
        <p className="muted">Rien pour l'instant.</p>
      ) : (
        <ol className="log">
          {entries.map(({ event, index }) => (
            <li key={index}>{describeEvent(event, game)}</li>
          ))}
        </ol>
      )}
    </section>
  )
}

export default EventLog
