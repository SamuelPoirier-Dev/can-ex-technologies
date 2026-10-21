// Remembers which player this tab is in a given game.
// sessionStorage is per tab, so several tabs of one browser can be different players.

export type Session = { playerId: string; token: string }

const key = (code: string) => `monopoly:${code.toUpperCase()}`

export function loadSession(code: string): Session | null {
  try {
    const raw = sessionStorage.getItem(key(code))
    return raw ? (JSON.parse(raw) as Session) : null
  } catch {
    return null
  }
}

export function saveSession(code: string, session: Session): void {
  try {
    sessionStorage.setItem(key(code), JSON.stringify(session))
  } catch {
    // Storage unavailable (e.g. private mode): the tab simply won't survive a reload.
  }
}
