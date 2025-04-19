export function parseFEN(fen) {
    const parts = fen.split(' ');
    const boardPart = parts[0];
    const rows = boardPart.split('/');
    
    const board = [];
    
    for (let i = 0; i < 8; i++) {
        const boardRow = [];
        let j = 0;
        
        for (let char of rows[i]) {
            if (isNaN(char)) {
                let piece = '';
                
                switch (char) {
                    case 'P': piece = 'wp'; break; 
                    case 'R': piece = 'wr'; break; 
                    case 'N': piece = 'wn'; break; 
                    case 'B': piece = 'wb'; break; 
                    case 'Q': piece = 'wq'; break; 
                    case 'K': piece = 'wk'; break;
                    case 'p': piece = 'bp'; break; 
                    case 'r': piece = 'br'; break; 
                    case 'n': piece = 'bn'; break; 
                    case 'b': piece = 'bb'; break; 
                    case 'q': piece = 'bq'; break; 
                    case 'k': piece = 'bk'; break; 
                }
                
                boardRow.push(piece);
                j++;
            } else {
                const emptySquares = parseInt(char);
                for (let k = 0; k < emptySquares; k++) {
                    boardRow.push(null);
                    j++;
                }
            }
        }
        
        board.push(boardRow);
    }
    
    return board;
}

export function renderPiece(piece) {
    if (!piece) return null;
    
    piece = piece.charAt(0) + piece.charAt(1).toUpperCase() + piece.slice(2);

    const imagePath = `/chess_pieces/${piece}.svg`;
    
    return (
        <div className="w-full h-full flex justify-center items-center">
            <img 
                src={imagePath} 
                alt={`${piece.color} ${piece.type}`} 
                className="w-4/5 h-4/5 object-contain"
            />
        </div>
    );
}

export const coordsToAlgebraic = (row, col) => {
    return columns[col] + rows[row];
};

const isLegalMove = (fromSquare, toSquare) => {
    const from = coordsToAlgebraic(fromSquare.row, fromSquare.col);
    const to = coordsToAlgebraic(toSquare.row, toSquare.col);
    
    return legalMoves.some(move => move.from === from && move.to === to);
};

const handleSquareClick = (row, col) => {
    const isMyTurn = currentTurn === playerColor;
    const piece = board[row][col];
    const pieceColor = piece && (piece.charAt(0) === 'w' ? 'white' : 'black');
    const isMyPiece = pieceColor === playerColor;
    
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.log("Cannot make move: socket not connected");
        return;
    }
    
    if (!isMyTurn) {
        console.log("Not your turn");
        return;
    }

    if (selectedSquare && selectedSquare.row === row && selectedSquare.col === col) {
        setSelectedSquare(null);
        return;
    }

    if (selectedSquare) {
        const toSquare = { row, col };
        
        if (isLegalMove(selectedSquare, toSquare)) {
            const from = coordsToAlgebraic(selectedSquare.row, selectedSquare.col);
            const to = coordsToAlgebraic(row, col);
            
            let promotion = null;
            const piece = board[selectedSquare.row][selectedSquare.col];
            
            if ((piece === 'wp' && row === 0) || (piece === 'bp' && row === 7)) {
                promotion = 'Q';
            }
            
            console.log(`Sending move: ${from} -> ${to}`);
            socket.send(JSON.stringify({
                action: 'make_move',
                move: {
                    from: from,
                    to: to,
                    promotion: promotion
                }
            }));
            
            setSelectedSquare(null);
        } else if (piece && isMyPiece) {
            setSelectedSquare({ row, col });
        } else {
            console.log("Invalid move");
            setSelectedSquare(null);
        }
    } else if (piece && isMyPiece) {
        setSelectedSquare({ row, col });
    }
};

const isLegalDestination = (row, col) => {
    if (!selectedSquare) return false;
    
    const from = coordsToAlgebraic(selectedSquare.row, selectedSquare.col);
    const to = coordsToAlgebraic(row, col);
    
    return legalMoves.some(move => move.from === from && move.to === to);
};

const getHighlightClass = (row, col) => {
    if (selectedSquare && selectedSquare.row === row && selectedSquare.col === col) {
        return 'border-4 border-yellow-500';
    }
    
    if (selectedSquare && isLegalDestination(row, col)) {
        const piece = board[row][col];
        if (piece) {
            return 'border-4 border-red-500';
        } else {
            return 'border-4 border-green-500';
        }
    }
    
    return '';
};
