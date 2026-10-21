import { useEffect, useState } from 'react'

import GameView from './components/GameView'
import Home from './components/Home'

// Two screens only, so no router: "/" is the home page, "/game/CODE" a game.
function codeFromUrl(): string | null {
  const match = window.location.pathname.match(/^\/game\/([A-Za-z0-9]+)\/?$/)
  return match ? match[1].toUpperCase() : null
}

function App() {
  const [code, setCode] = useState(codeFromUrl)

  useEffect(() => {
    const onPopState = () => setCode(codeFromUrl())
    window.addEventListener('popstate', onPopState)
    return () => window.removeEventListener('popstate', onPopState)
  }, [])

  const openGame = (gameCode: string) => {
    const normalized = gameCode.trim().toUpperCase()
    window.history.pushState(null, '', `/game/${normalized}`)
    setCode(normalized)
  }

  return code ? <GameView key={code} code={code} /> : <Home onOpenGame={openGame} />
}

export default App
