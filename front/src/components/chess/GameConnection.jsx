import { useState, useEffect } from 'react';
import { GameStatus } from './ChessTypes';

const useGameConnection = (onBoardUpdate, onGameStateUpdate) => {
    const [socket, setSocket] = useState(null);
    const [gameStatus, setGameStatus] = useState(GameStatus.CONNECTING);
    const [playerColor, setPlayerColor] = useState(null);
    const [currentTurn, setCurrentTurn] = useState('white');
    const [legalMoves, setLegalMoves] = useState([]);

    const connectToGame = (gameId, isNewGame = false) => {
        const newSocket = new WebSocket(`ws://localhost:8000/ws/${gameId}`);
        
        newSocket.onopen = () => {
            console.log("WebSocket connection established.");
            setGameStatus(GameStatus.CONNECTED);
            
            if (isNewGame) {
                setPlayerColor('white');
            } else {
                setPlayerColor('black');
                newSocket.send(JSON.stringify({ action: 'join_game' }));
            }
            
            newSocket.send(JSON.stringify({ action: 'get_board' }));
        };
        
        newSocket.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                
                if (message.fen) {
                    onBoardUpdate(message.fen);
                }
                
                if (message.status) {
                    setGameStatus(message.status);
                }
                
                if (message.turn) {
                    setCurrentTurn(message.turn);
                }
                
                if (message.legalMoves) {
                    setLegalMoves(message.legalMoves);
                }
                
                if (message.gameState) {
                    onGameStateUpdate(message.gameState);
                    if (message.gameState !== "ongoing") {
                        setGameStatus(`Game over - ${message.gameState}`);
                    }
                }
                
                if (message.error) {
                    console.error("Server error:", message.error);
                    alert(`Error: ${message.error}`);
                }
            } catch (error) {
                console.error("Error processing message:", error);
            }
        };
        
        newSocket.onerror = (error) => {
            console.error("WebSocket error:", error);
            setGameStatus(GameStatus.ERROR);
        };
        
        newSocket.onclose = () => {
            console.log("WebSocket connection closed.");
            setGameStatus(GameStatus.DISCONNECTED);
        };
        
        setSocket(newSocket);
    };

    useEffect(() => {
        return () => {
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.close();
            }
        };
    }, [socket]);

    const makeMove = (from, to, promotion = null) => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                action: 'make_move',
                move: { from, to, promotion }
            }));
        }
    };

    return {
        socket,
        gameStatus,
        playerColor,
        currentTurn,
        legalMoves,
        connectToGame,
        makeMove
    };
};

export default useGameConnection; 