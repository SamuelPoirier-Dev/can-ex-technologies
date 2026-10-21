import { useEffect, useState } from 'react'

type Health = { status: string }

function App() {
  const [status, setStatus] = useState('checking...')

  useEffect(() => {
    fetch('/api/health')
      .then((response) => response.json() as Promise<Health>)
      .then((health) => setStatus(health.status))
      .catch(() => setStatus('unreachable'))
  }, [])

  return (
    <main>
      <h1>Monopoly</h1>
      <p>Backend: {status}</p>
    </main>
  )
}

export default App
