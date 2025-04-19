export const columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
export const rows = ['8', '7', '6', '5', '4', '3', '2', '1'];

export const initialFEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';

export const GameStatus = {
    CONNECTING: "connecting",
    CONNECTED: "connected",
    DISCONNECTED: "disconnected",
    ERROR: "error",
    GAME_OVER: "game over"
};

export const GameState = {
    ONGOING: "ongoing",
    CHECKMATE: "checkmate",
    STALEMATE: "stalemate",
    DRAW: "draw"
}; 