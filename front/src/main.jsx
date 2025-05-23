import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import ChessBoard from './components/chess/ChessBoard.jsx'
import ClobberBoard from './components/clobber/ClobberBoard.jsx'
import TicTacToeBoard from './components/tictactoe/tictactoe_board.jsx'
import GameHub from './components/game_hub.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <GameHub />
  </StrictMode>,
)
