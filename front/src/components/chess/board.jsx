import { useState } from "react";
import { initializeBoard, renderPiece } from './initialize_board.jsx';
import '../../index.css'

function ChessBoard() {
    const columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']; 
    const rows = ['8', '7', '6', '5', '4', '3', '2', '1'];
    
    const [board, setBoard] = useState(initializeBoard());
    const [selectedSquare, setSelectedSquare] = useState(null);

    const handleSquareClick = (row, col) => {
        if (selectedSquare && selectedSquare.row === row && selectedSquare.col === col) {
            setSelectedSquare(null);
            return;
        }
        
        if (selectedSquare) {
            const newBoard = board.map(row => [...row]);
            newBoard[row][col] = board[selectedSquare.row][selectedSquare.col];
            newBoard[selectedSquare.row][selectedSquare.col] = null;
            setBoard(newBoard);
            setSelectedSquare(null);
        } else if (board[row][col]) {
            setSelectedSquare({ row, col });
        }
    };

    const getHighlightClass = (row, col) => {
        const isSelected = selectedSquare && selectedSquare.row === row && selectedSquare.col === col;
        
        if (isSelected) {
            return 'border-4 border-yellow-500';
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
                        
                        <div className="grid grid-cols-8 grid-rows-8 w-[600px] h-[600px] border-4 border-gray-600">
                            {board.flat().map((piece, index) => {
                                const row = Math.floor(index / 8);
                                const col = index % 8;
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

export default ChessBoard;
