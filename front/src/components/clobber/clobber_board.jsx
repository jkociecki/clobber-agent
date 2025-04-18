import { useState } from "react";
import '../../index.css'

function ClobberBoard() {
    const columns = ['a', 'b', 'c', 'd', 'e', 'f'];
    const rows = ['6', '5', '4', '3', '2', '1'];
    
    const initializeClobberBoard = () => {
        const board = Array(6).fill().map(() => Array(6).fill(null));
        
        for (let row = 0; row < 6; row++) {
            for (let col = 0; col < 6; col++) {
                if ((row + col) % 2 === 0) {
                    board[row][col] = 'white';
                } else {
                    board[row][col] = 'black';
                }
            }
        }
        
        return board;
    };
    
    const renderPiece = (piece) => {
        if (!piece) return null;
        
        if (piece === 'white') {
            return (
                <div className="w-10 h-10 rounded-full bg-white border-2 border-gray-300 shadow-md"></div>
            );
        } else if (piece === 'black') {
            return (
                <div className="w-10 h-10 rounded-full bg-gray-800 border-2 border-gray-700 shadow-md"></div>
            );
        }
        
        return null;
    };
    
    const [board, setBoard] = useState(initializeClobberBoard());
    const [selectedSquare, setSelectedSquare] = useState(null);
    const [currentPlayer, setCurrentPlayer] = useState('white');
    
    const isValidMove = (fromRow, fromCol, toRow, toCol) => {
        const rowDiff = Math.abs(fromRow - toRow);
        const colDiff = Math.abs(fromCol - toCol);
        
        if (!((rowDiff === 1 && colDiff === 0) || (rowDiff === 0 && colDiff === 1))) {
            return false;
        }
        
        const fromPiece = board[fromRow][fromCol];
        const toPiece = board[toRow][toCol];
        
        if (!toPiece || fromPiece === toPiece) {
            return false;
        }
        
        return true;
    };
    
    const handleSquareClick = (row, col) => {
        if (selectedSquare && selectedSquare.row === row && selectedSquare.col === col) {
            setSelectedSquare(null);
            return;
        }
        
        if (selectedSquare) {
            if (isValidMove(selectedSquare.row, selectedSquare.col, row, col)) {
                const newBoard = board.map(r => [...r]);
                newBoard[row][col] = board[selectedSquare.row][selectedSquare.col];
                newBoard[selectedSquare.row][selectedSquare.col] = null;
                setBoard(newBoard);
                
                setCurrentPlayer(currentPlayer === 'white' ? 'black' : 'white');
            }
            setSelectedSquare(null);
        } else if (board[row][col] === currentPlayer) {
            setSelectedSquare({ row, col });
        }
    };
    
    const getHighlightClass = (row, col) => {
        const isSelected = selectedSquare && selectedSquare.row === row && selectedSquare.col === col;
        
        if (isSelected) {
            return 'border-4 border-yellow-500';
        }
        
        if (selectedSquare) {
            if (isValidMove(selectedSquare.row, selectedSquare.col, row, col)) {
                return 'border-4 border-green-500';
            }
        }
        
        return '';
    };
    
    return (
        <div className="flex justify-center items-center h-screen bg-gradient-to-b from-gray-800 to-gray-900">
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
                            {board.flat().map((piece, index) => {
                                const row = Math.floor(index / 6);
                                const col = index % 6;
                                const isLightSquare = (row + col) % 2 === 0;
                                const highlightClass = getHighlightClass(row, col);

                                return (
                                    <div
                                        key={index}
                                        onClick={() => handleSquareClick(row, col)}
                                        className={`w-[75px] h-[75px] ${
                                            isLightSquare 
                                                ? 'bg-[#eeeed2]' 
                                                : 'bg-[#769656]'
                                        } ${highlightClass} 
                                        transition-colors duration-200 flex justify-center items-center
                                        cursor-pointer hover:opacity-90`}
                                    >
                                        {renderPiece(piece)}
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ClobberBoard;
