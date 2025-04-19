import { useState, useEffect } from 'react';
import { GameStatus } from './ClobberTypes';

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
            setGameStatus(GameStatus.CONNECTING);
            
            if (isNewGame) {
                setPlayerColor('black'); 
                setCurrentTurn('black');  
            } else {
                setPlayerColor('white'); 
                setCurrentTurn('black');  
                newSocket.send(JSON.stringify({ action: 'join_game' }));
            }
        };
        
        newSocket.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                console.log("Received message:", message); 
                
                if (message.board) {

                    const convertedBoard = message.board.map(row => 
                        row.map(pieceValue => {
                            if (pieceValue === 0) return 'white';
                            if (pieceValue === 1) return 'black';
                            return null;
                        })
                    );
                    console.log("Converted board:", convertedBoard);  
                    onBoardUpdate(convertedBoard);
                    setGameStatus(GameStatus.CONNECTED);
                }
                
                if (message.status) {
                    console.log("Updating status to:", message.status);  
                    setGameStatus(message.status);
                }
                
                if (message.turn) {
                    console.log("Updating turn to:", message.turn);  
                    console.log("Current player color:", playerColor); 
                    setCurrentTurn(message.turn);
                }
                
                if (message.legalMoves) {
                    console.log("Updating legal moves:", message.legalMoves);  
                    setLegalMoves(message.legalMoves);
                }
                
                if (message.gameState) {
                    console.log("Updating game state:", message.gameState);  
                    onGameStateUpdate(message.gameState);
                    if (message.gameState !== "ongoing") {
                        setGameStatus(`Game over - ${message.gameState}`);
                    }
                }
                
                if (message.error) {
                    console.error("Server error:", message.error);
                    alert(`Error: ${message.error}`);
                }

                console.log("Current game state:", {
                    playerColor,
                    currentTurn: message.turn || currentTurn,
                    legalMoves: message.legalMoves || legalMoves,
                    gameStatus
                });
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

    const makeMove = (from, to) => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                action: 'make_move',
                move: { from, to }
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