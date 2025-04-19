import { useState } from 'react';
import { columns, rows, PieceType } from './ClobberTypes';
import ClobberSquare from './ClobberSquare';
import GameControls from './GameControls';
import useGameConnection from './GameConnection';

const ClobberBoard = () => {
    const initializeBoard = () => {
        const board = Array(6).fill().map(() => Array(6).fill(null));
        
        for (let row = 0; row < 6; row++) {
            for (let col = 0; col < 6; col++) {
                if ((row + col) % 2 === 0) {
                    board[row][col] = PieceType.WHITE;
                } else {
                    board[row][col] = PieceType.BLACK;
                }
            }
        }
        
        return board;
    };

    const [board, setBoard] = useState(initializeBoard());
    const [selectedSquare, setSelectedSquare] = useState(null);
    const [showJoinForm, setShowJoinForm] = useState(true);
    const [gameState, setGameState] = useState("ongoing");
    const [gameId, setGameId] = useState(null);

    const {
        socket,
        gameStatus,
        playerColor,
        currentTurn,
        legalMoves,
        connectToGame,
        makeMove
    } = useGameConnection(
        (newBoard) => setBoard(newBoard),
        (state) => setGameState(state)
    );

    const createNewGame = async () => {
        try {
            const response = await fetch("http://localhost:8000/new_game/");
            const data = await response.json();
            setGameId(data.game_id);
            setShowJoinForm(false);
            connectToGame(data.game_id, true);
        } catch (error) {
            console.error("Error creating new game:", error);
        }
    };

    const joinGame = (gameId) => {
        if (gameId) {
            setGameId(gameId);
            setShowJoinForm(false);
            connectToGame(gameId, false);
        }
    };

    const coordsToAlgebraic = (row, col) => {
        return columns[col] + rows[row];
    };

    const isLegalMove = (fromSquare, toSquare) => {
        const from = coordsToAlgebraic(fromSquare.row, fromSquare.col);
        const to = coordsToAlgebraic(toSquare.row, toSquare.col);
        return legalMoves.some(move => 
            move.from === from && move.to === to
        );
    };

    const handleSquareClick = (row, col) => {
        if (!socket || socket.readyState !== WebSocket.OPEN) {
            return;
        }

        if (selectedSquare && selectedSquare.row === row && selectedSquare.col === col) {
            setSelectedSquare(null);
            return;
        }

        if (selectedSquare) {
            if (isLegalMove(selectedSquare, { row, col })) {
                const from = coordsToAlgebraic(selectedSquare.row, selectedSquare.col);
                const to = coordsToAlgebraic(row, col);
                makeMove(from, to);
            }
            setSelectedSquare(null);
        } else if (board[row][col] === playerColor && currentTurn === playerColor) {
            setSelectedSquare({ row, col });
        }
    };

    const isLegalDestination = (row, col) => {
        if (!selectedSquare) return false;
        return isLegalMove(selectedSquare, { row, col });
    };

    if (showJoinForm) {
        return <GameControls onCreateGame={createNewGame} onJoinGame={joinGame} />;
    }

    return (
        <div className="flex flex-col justify-center items-center h-screen bg-gradient-to-b from-gray-800 to-gray-900">
            <div className="mb-4 text-gray-300">
                <div className="mb-1">Status: {gameStatus}</div>
                <div className="mb-1">ID gry: {gameId} <button onClick={() => {navigator.clipboard.writeText(gameId)}} className="bg-blue-600 hover:bg-blue-700 text-white py-1 px-2 rounded text-sm ml-2">Kopiuj</button></div>
                <div className="mb-1">Grasz jako: {playerColor}</div>
                <div className="mb-1">Tura: {currentTurn} {gameState !== "ongoing" ? `(${gameState})` : ""}</div>
            </div>
            
            <div className="p-8 bg-gray-700 rounded-lg shadow-2xl">
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
                        
                        <div className="grid grid-cols-6 grid-rows-6 w-[450px] h-[450px] border-4 border-gray-600">
                            {board.map((row, rowIndex) =>
                                row.map((piece, colIndex) => (
                                    <ClobberSquare
                                        key={`${rowIndex}-${colIndex}`}
                                        row={rowIndex}
                                        col={colIndex}
                                        piece={piece}
                                        isSelected={selectedSquare?.row === rowIndex && selectedSquare?.col === colIndex}
                                        isLegalMove={isLegalDestination(rowIndex, colIndex)}
                                        onClick={handleSquareClick}
                                    />
                                ))
                            )}
                        </div>
                    </div>  
                </div>
            </div>
        </div>
    );
};

export default ClobberBoard; 
