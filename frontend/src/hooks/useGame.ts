import { useEffect, useState } from 'react'

import type { Game, LiveMessage } from '../api/types'

// Close code sent by the backend for an unknown game (see backend/app/api/live.py).
const CLOSE_GAME_NOT_FOUND = 4404
const RECONNECT_DELAY_MS = 1000

/** Subscribes to a game's live state. The WebSocket is the only source of displayed state. */
export function useGame(code: string): { game: Game | null; notFound: boolean } {
  const [game, setGame] = useState<Game | null>(null)
  const [notFound, setNotFound] = useState(false)

  useEffect(() => {
    let socket: WebSocket | null = null
    let retryTimer: number | undefined
    let stopped = false

    const connect = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
      socket = new WebSocket(`${protocol}://${window.location.host}/ws/games/${code}`)

      socket.onmessage = (event: MessageEvent<string>) => {
        const message = JSON.parse(event.data) as LiveMessage
        if (message.type === 'state') setGame(message.game)
      }

      socket.onclose = (event) => {
        if (stopped) return
        if (event.code === CLOSE_GAME_NOT_FOUND) {
          setNotFound(true)
          return
        }
        retryTimer = window.setTimeout(connect, RECONNECT_DELAY_MS)
      }
    }

    connect()
    return () => {
      stopped = true
      window.clearTimeout(retryTimer)
      socket?.close()
    }
  }, [code])

  return { game, notFound }
}
