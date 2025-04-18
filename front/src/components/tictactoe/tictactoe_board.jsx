import { useState } from "react";
import '../../index.css'

function TicTacToeBoard() {
    const columns = ['a', 'b', 'c', 'd', 'e'];
    const rows = ['5', '4', '3', '2', '1'];
    
    const initializeTicTacToeBoard = () => {
        return Array(5).fill().map(() => Array(5).fill(null));
    };
    
    const [board, setBoard] = useState(initializeTicTacToeBoard());
    const [currentPlayer, setCurrentPlayer] = useState('X');
    const [gameOver, setGameOver] = useState(false);
    const [winner, setWinner] = useState(null);
    
    const renderPiece = (piece) => {
        if (!piece) return null;
        
        if (piece === 'X') {
            return (
                <div className="text-5xl font-bold text-blue-600">✕</div>
            );
        } else if (piece === 'O') {
            return (
                <div className="text-5xl font-bold text-red-600">◯</div>
            );
        }
        
        return null;
    };
    
    const checkWinner = (board, row, col) => {
        const piece = board[row][col];
        if (!piece) return null;
        
        let count = 0;
        for (let c = 0; c < 5; c++) {
            if (board[row][c] === piece) {
                count++;
                if (count === 5) return piece;
            } else {
                count = 0;
            }
        }
        
        count = 0;
        for (let r = 0; r < 5; r++) {
            if (board[r][col] === piece) {
                count++;
                if (count === 5) return piece;
            } else {
                count = 0;
            }
        }
        
        count = 0;
        for (let i = -4; i <= 4; i++) {
            const r = row + i;
            const c = col + i;
            if (r >= 0 && r < 5 && c >= 0 && c < 5) {
                if (board[r][c] === piece) {
                    count++;
                    if (count === 5) return piece;
                } else {
                    count = 0;
                }
            }
        }
        
        count = 0;
        for (let i = -4; i <= 4; i++) {
            const r = row + i;
            const c = col - i;
            if (r >= 0 && r < 5 && c >= 0 && c < 5) {
                if (board[r][c] === piece) {
                    count++;
                    if (count === 5) return piece;
                } else {
                    count = 0;
                }
            }
        }
        
        let isBoardFull = true;
        for (let r = 0; r < 5; r++) {
            for (let c = 0; c < 5; c++) {
                if (!board[r][c]) {
                    isBoardFull = false;
                    break;
                }
            }
            if (!isBoardFull) break;
        }
        
        if (isBoardFull) return 'remis';
        
        return null;
    };
    
    const handleSquareClick = (row, col) => {
        if (gameOver || board[row][col]) {
            return;
        }
        
        const newBoard = board.map(r => [...r]);
        newBoard[row][col] = currentPlayer;
        setBoard(newBoard);
        
        const gameWinner = checkWinner(newBoard, row, col);
        if (gameWinner) {
            setGameOver(true);
            setWinner(gameWinner);
            return;
        }
        
        setCurrentPlayer(currentPlayer === 'X' ? 'O' : 'X');
    };
    
    const resetGame = () => {
        setBoard(initializeTicTacToeBoard());
        setCurrentPlayer('X');
        setGameOver(false);
        setWinner(null);
    };
    
    return (
        <div className="flex justify-center items-center h-screen bg-gradient-to-b from-gray-800 to-gray-900">
            <div className="p-8 bg-gray-700 rounded-lg shadow-2xl">
                <div className="mb-4 text-center text-white text-xl">
                    {gameOver 
                        ? (winner === 'remis' 
                            ? 'Remis!' 
                            : `Zwycięzca: ${winner === 'X' ? 'X (niebieski)' : 'O (czerwony)'}`) 
                        : `Ruch gracza: ${currentPlayer === 'X' ? 'X (niebieski)' : 'O (czerwony)'}`}
                </div>
                <div className="relative">
                    <div className="flex justify-around mb-1">
                        {columns.map((col) => (
                            <div key={col} className="w-[75px] text-center text-gray-300">
                                {col}
                            </div>
                        ))}
                    </div>
                    
                    <div className="flex">
                        <div className="flex flex-col justify-around mr-1">
                            {rows.map((row) => (
                                <div key={row} className="h-[75px] flex items-center text-gray-300">
                                    {row}
                                </div>
                            ))}
                        </div>
                        
                        <div className="grid grid-cols-5 grid-rows-5 w-[375px] h-[375px] border-4 border-gray-600">
                            {board.flat().map((piece, index) => {
                                const row = Math.floor(index / 5);
                                const col = index % 5;
                                const isLightSquare = (row + col) % 2 === 0;

                                return (
                                    <div
                                        key={index}
                                        onClick={() => handleSquareClick(row, col)}
                                        className={`w-[75px] h-[75px] ${
                                            isLightSquare 
                                                ? 'bg-[#eeeed2]' 
                                                : 'bg-[#769656]'
                                        } 
                                        transition-colors duration-200 flex justify-center items-center
                                        cursor-pointer hover:opacity-90`}
                                    >
                                        {renderPiece(piece)}
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                    
                    <div className="mt-4 flex justify-center">
                        <button 
                            onClick={resetGame}
                            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                        >
                            Nowa gra
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default TicTacToeBoard;
