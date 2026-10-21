import { useState } from 'react'

import { playTurn } from '../api/client'
import { loadSession, type Session } from '../api/session'
import type { Game } from '../api/types'
import { useGame } from '../hooks/useGame'
import { lastRoll } from '../lib/events'
import { playerName } from '../lib/players'
import Board from './Board'
import EventLog from './EventLog'
import JoinForm from './JoinForm'
import Players from './Players'

type Props = { code: string }

function GameView({ code }: Props) {
  const { game, notFound } = useGame(code)
  const [session, setSession] = useState<Session | null>(() => loadSession(code))

  if (notFound) {
    return (
      <main className="page">
        <p className="error">Partie introuvable : {code}</p>
        <a href="/">Retour à l'accueil</a>
      </main>
    )
  }
  if (!game) {
    return <main className="page muted">Connexion à la partie…</main>
  }

  const myId = session?.playerId ?? null
  const canJoin = !session && game.status === 'waiting'

  return (
    <main className="page">
      <header className="game-header">
        <h1>
          <a href="/">Monopoly Québec</a>
        </h1>
        <span className="muted">
          Partie <strong>{game.id}</strong>
          {!session && game.status !== 'waiting' && ' · spectateur'}
        </span>
      </header>

      {game.status === 'waiting' && <WaitingBanner game={game} />}
      {game.winner_id && (
        <p className="banner winner">{playerName(game, game.winner_id)} gagne la partie !</p>
      )}
      {canJoin && <JoinForm code={game.id} onJoined={setSession} />}

      <div className="game-layout">
        <Board game={game}>
          <TurnPanel game={game} session={session} />
        </Board>
        <aside className="side">
          <Players game={game} myId={myId} />
          <EventLog game={game} />
        </aside>
      </div>
    </main>
  )
}

function WaitingBanner({ game }: { game: Game }) {
  const link = `${window.location.origin}/game/${game.id}`
  return (
    <div className="banner">
      En attente de joueurs ({game.players.length}/{game.max_players}). Partage le code{' '}
      <strong>{game.id}</strong> ou le lien <code>{link}</code>
    </div>
  )
}

function TurnPanel({ game, session }: { game: Game; session: Session | null }) {
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const roll = lastRoll(game)

  if (game.status !== 'in_progress' || !game.current_player_id) {
    return <div className="turn">{roll !== null && <Dice value={roll} />}</div>
  }

  const myTurn = session?.playerId === game.current_player_id

  const handleRoll = async () => {
    if (!session) return
    setBusy(true)
    setError(null)
    try {
      await playTurn(game.id, session.token)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="turn">
      {roll !== null && <Dice value={roll} />}
      {myTurn ? (
        <button onClick={handleRoll} disabled={busy}>
          Lancer le dé
        </button>
      ) : (
        <p>Tour de {playerName(game, game.current_player_id)}</p>
      )}
      {error && <p className="error">{error}</p>}
    </div>
  )
}

function Dice({ value }: { value: number }) {
  return (
    <div className="dice" aria-label={`Dernier lancer : ${value}`}>
      {value}
    </div>
  )
}

export default GameView
