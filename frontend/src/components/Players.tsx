import type { Game } from '../api/types'
import { playerColor } from '../lib/players'

type Props = { game: Game; myId: string | null }

function Players({ game, myId }: Props) {
  return (
    <section className="card">
      <h2>Joueurs</h2>
      <ul className="players">
        {game.players.map((player) => {
          const isCurrent = player.id === game.current_player_id
          const classes = ['player', isCurrent && 'current', player.is_bankrupt && 'bankrupt']
          return (
            <li key={player.id} className={classes.filter(Boolean).join(' ')}>
              <div className="player-header">
                <span className="pawn" style={{ background: playerColor(game, player.id) }} />
                <strong>{player.name}</strong>
                {player.id === myId && <span className="tag">toi</span>}
                {player.id === game.winner_id && <span className="tag">gagnant</span>}
                {player.is_bankrupt && <span className="tag">faillite</span>}
                <span className="money">{player.money} $</span>
              </div>
              {player.properties.length > 0 && (
                <ul className="properties">
                  {player.properties.map((index) => (
                    <li key={index}>{game.board[index].name}</li>
                  ))}
                </ul>
              )}
            </li>
          )
        })}
      </ul>
    </section>
  )
}

export default Players
