import type { ReactNode } from 'react'

import type { Game } from '../api/types'
import { gridSize, ringCell } from '../lib/board'
import { playerColor, playerName } from '../lib/players'

type Props = { game: Game; children?: ReactNode }

/** The board as a ring of squares; `children` is drawn in the middle. */
function Board({ game, children }: Props) {
  const size = gridSize(game.board.length)
  const activePlayers = game.players.filter((p) => !p.is_bankrupt)

  return (
    <div
      className="board"
      style={{ gridTemplateColumns: `repeat(${size}, 1fr)`, gridTemplateRows: `repeat(${size}, 1fr)` }}
    >
      {game.board.map((square) => {
        const cell = ringCell(square.index, game.board.length)
        const owner = square.owner_id
        const pawns = activePlayers.filter((p) => p.position === square.index)
        return (
          <div
            key={square.index}
            className={`square${square.price === null ? ' empty' : ''}`}
            style={{
              gridRow: cell.row,
              gridColumn: cell.column,
              borderColor: owner ? playerColor(game, owner) : undefined,
            }}
            title={owner ? `Propriété de ${playerName(game, owner)}` : undefined}
          >
            <span className="square-name">{square.name}</span>
            {square.price !== null && <span className="square-price">{square.price} $</span>}
            <span className="pawns">
              {pawns.map((p) => (
                <span
                  key={p.id}
                  className="pawn"
                  style={{ background: playerColor(game, p.id) }}
                  title={p.name}
                />
              ))}
            </span>
          </div>
        )
      })}
      <div className="board-center" style={{ gridRow: `2 / ${size}`, gridColumn: `2 / ${size}` }}>
        {children}
      </div>
    </div>
  )
}

export default Board
