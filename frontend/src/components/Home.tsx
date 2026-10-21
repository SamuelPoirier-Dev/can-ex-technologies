import { useState, type FormEvent } from 'react'

import { createGame } from '../api/client'
import { saveSession } from '../api/session'

type Props = { onOpenGame: (code: string) => void }

function Home({ onOpenGame }: Props) {
  const [name, setName] = useState('')
  const [maxPlayers, setMaxPlayers] = useState(2)
  const [code, setCode] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const handleCreate = async (event: FormEvent) => {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      const created = await createGame(name, maxPlayers)
      saveSession(created.game.id, { playerId: created.player_id, token: created.token })
      onOpenGame(created.game.id)
    } catch (e) {
      setError((e as Error).message)
      setBusy(false)
    }
  }

  const handleJoin = (event: FormEvent) => {
    event.preventDefault()
    onOpenGame(code)
  }

  return (
    <main className="home">
      <h1>Monopoly Québec</h1>

      <form className="card" onSubmit={handleCreate}>
        <h2>Créer une partie</h2>
        <label>
          Ton nom
          <input value={name} onChange={(e) => setName(e.target.value)} maxLength={20} required />
        </label>
        <label>
          Nombre de joueurs
          <select value={maxPlayers} onChange={(e) => setMaxPlayers(Number(e.target.value))}>
            {[2, 3, 4].map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
          </select>
        </label>
        <button type="submit" disabled={busy}>
          Créer
        </button>
        {error && <p className="error">{error}</p>}
      </form>

      <form className="card" onSubmit={handleJoin}>
        <h2>Rejoindre une partie</h2>
        <label>
          Code de la partie
          <input
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="ABC234"
            maxLength={6}
            required
          />
        </label>
        <button type="submit">Rejoindre</button>
      </form>
    </main>
  )
}

export default Home
