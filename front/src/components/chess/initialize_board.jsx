export function initializeBoard() {
    const board = Array(8).fill().map(() => Array(8).fill(null));
    
    board[0][0] = "BR";
    board[0][1] = "BN";
    board[0][2] = "BB";
    board[0][3] = "BQ";
    board[0][4] = "BK";
    board[0][5] = "BB";
    board[0][6] = "BN";
    board[0][7] = "BR";
    
    for (let col = 0; col < 8; col++) {
        board[1][col] = "BP";
    }
    
    board[7][0] = "WR";
    board[7][1] = "WN";
    board[7][2] = "WB";
    board[7][3] = "WQ";
    board[7][4] = "WK";
    board[7][5] = "WB";
    board[7][6] = "WN";
    board[7][7] = "WR";
    
    for (let col = 0; col < 8; col++) {
        board[6][col] = "WP";
    }
    
    return board;
}

export function renderPiece(piece) {
    if (!piece) return null;
    
    const pieceMapping = {
        "WP": "♙",
        "WR": "♖",
        "WN": "♘",
        "WB": "♗",
        "WQ": "♕",
        "WK": "♔",
        "BP": "♟",
        "BR": "♜",
        "BN": "♞",
        "BB": "♝",
        "BQ": "♛",
        "BK": "♚"
    };
    
    const pieceSymbol = pieceMapping[piece];
    const pieceColor = piece[0] === "W" ? "text-white" : "text-black";
    
    return (
        <div className={`text-5xl ${pieceColor}`}>
            {pieceSymbol}
        </div>
    );
}
