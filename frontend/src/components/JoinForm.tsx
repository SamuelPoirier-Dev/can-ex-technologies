import { useState, type FormEvent } from 'react'

import { joinGame } from '../api/client'
import { saveSession, type Session } from '../api/session'

type Props = { code: string; onJoined: (session: Session) => void }

function JoinForm({ code, onJoined }: Props) {
  const [name, setName] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      const joined = await joinGame(code, name)
      const session = { playerId: joined.player_id, token: joined.token }
      saveSession(code, session)
      onJoined(session)
    } catch (e) {
      setError((e as Error).message)
      setBusy(false)
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h2>Rejoindre la partie</h2>
      <label>
        Ton nom
        <input value={name} onChange={(e) => setName(e.target.value)} maxLength={20} required />
      </label>
      <button type="submit" disabled={busy}>
        Rejoindre
      </button>
      {error && <p className="error">{error}</p>}
    </form>
  )
}

export default JoinForm
