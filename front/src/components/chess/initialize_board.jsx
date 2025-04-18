import React from 'react';

export function initializeBoard(fen_string) {
    const fen = fen_string || 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
    const emptyBoard = Array(8).fill(null).map(() => Array(8).fill(null));
    const board_fen = fen.split(' ')[0].split('/');

    for (let i = 0; i < 8; i++) {
        let col = 0;
        
        for (let j = 0; j < board_fen[i].length; j++) {
            const char = board_fen[i][j];
            
            if (!isNaN(parseInt(char))) {
                col += parseInt(char);
            } else {
                const color = char === char.toUpperCase() ? 'white' : 'black';
                let type = '';
                
                switch (char.toLowerCase()) {
                    case 'p': type = 'pawn'; break;
                    case 'r': type = 'rook'; break;
                    case 'n': type = 'knight'; break;
                    case 'b': type = 'bishop'; break;
                    case 'q': type = 'queen'; break;
                    case 'k': type = 'king'; break;
                }
                
                emptyBoard[i][col] = { type, color };
                col++;
            }
        }
    }
    
    return emptyBoard;
};

export function renderPiece(piece) {
    if (!piece) return null;
    
    const pieceMap = {
        'pawn': 'P',
        'rook': 'R',
        'knight': 'N',
        'bishop': 'B',
        'queen': 'Q',
        'king': 'K'
    };
    
    const colorPrefix = piece.color === 'white' ? 'w' : 'b';
    const pieceType = pieceMap[piece.type];
    const imagePath = `/chess_pieces/${colorPrefix}${pieceType}.svg`;
    
    const colorPrefix = piece.color === 'white' ? 'w' : 'b';
    const pieceType = pieceMap[piece.type];
    const imagePath = `/chess_pieces/${colorPrefix}${pieceType}.svg`;
    
    return (
        <div className="w-full h-full flex justify-center items-center">
            <img 
                src={imagePath} 
                alt={`${piece.color} ${piece.type}`} 
                className="w-4/5 h-4/5 object-contain"
            />
        </div>
    );
};