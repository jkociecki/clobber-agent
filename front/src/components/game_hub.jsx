import { useState } from "react";
import ChessBoard from "./chess/board.jsx";
import ClobberBoard from "./clobber/clobber_board.jsx";
import TicTacToeBoard from "./tictactoe/tictactoe_board.jsx";
import '../index.css';

function GameHub() {
    const [selectedGame, setSelectedGame] = useState(null);
    
    const games = [
        {
            id: "chess",
            title: "Szachy",
            description: "Klasyczna gra w szachy na planszy 8x8, w której celem jest danie mata królowi przeciwnika.",
            component: <ChessBoard />,
            iconEmoji: "♟️"
        },
        {
            id: "clobber",
            title: "Clobber",
            description: "Strategiczna gra na planszy 6x6, w której zbijasz pionki przeciwnika, stając na ich miejscu.",
            component: <ClobberBoard />,
            iconEmoji: "⚪"
        },
        {
            id: "tictactoe",
            title: "Kółko i Krzyżyk 5x5",
            description: "Rozszerzona wersja kółka i krzyżyka, gdzie wygrywa gracz, który ułoży 5 swoich symboli w jednej linii.",
            component: <TicTacToeBoard />,
            iconEmoji: "❌"
        }
    ];
    
    if (selectedGame) {
        return (
            <div>
                <div className="fixed top-4 left-4 z-10">
                    <button 
                        onClick={() => setSelectedGame(null)}
                        className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 
                                 transition-colors flex items-center space-x-2 shadow-lg"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L7.414 9H15a1 1 0 110 2H7.414l2.293 2.293a1 1 0 010 1.414z" clipRule="evenodd" />
                        </svg>
                        <span>Powrót do menu</span>
                    </button>
                </div>
                {games.find(game => game.id === selectedGame).component}
            </div>
        );
    }
    
    return (
        <div className="min-h-screen bg-gradient-to-b from-gray-800 to-gray-900 flex flex-col items-center justify-center p-8">
            <div className="text-center mb-8">
                <h1 className="text-4xl font-bold text-white mb-2">Centrum Gier Planszowych</h1>
                <p className="text-gray-300">Wybierz jedną z dostępnych gier planszowych</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl">
                {games.map((game) => (
                    <div 
                        key={game.id}
                        onClick={() => setSelectedGame(game.id)}
                        className="bg-gray-700 rounded-lg shadow-xl overflow-hidden transition-transform 
                                 hover:transform hover:scale-105 cursor-pointer"
                    >
                        <div className="bg-gray-600 p-8 flex justify-center items-center">
                            <span className="text-6xl">{game.iconEmoji}</span>
                        </div>
                        <div className="p-6">
                            <h2 className="text-2xl font-bold text-white mb-2">{game.title}</h2>
                            <p className="text-gray-300 mb-4">{game.description}</p>
                            <button 
                                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 
                                         rounded transition-colors"
                            >
                                Zagraj teraz
                            </button>
                        </div>
                    </div>
                ))}
            </div>
            
            <footer className="mt-12 text-gray-400 text-center">
                <p>© 2025 Centrum Gier Planszowych | Wszystkie prawa zastrzeżone</p>
            </footer>
        </div>
    );
}

export default GameHub;
