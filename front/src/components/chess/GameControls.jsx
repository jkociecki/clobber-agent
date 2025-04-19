import { useState } from 'react';

const GameControls = ({ onCreateGame, onJoinGame }) => {
    const [joinGameId, setJoinGameId] = useState("");

    return (
        <div className="flex flex-col justify-center items-center h-screen bg-gradient-to-b from-gray-800 to-gray-900">
            <div className="p-8 bg-gray-700 rounded-lg shadow-2xl text-gray-300">
                <h1 className="text-2xl mb-6 text-center">Szachy Online</h1>
                
                <div className="mb-6">
                    <button 
                        onClick={onCreateGame}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded"
                    >
                        Utwórz nową grę
                    </button>
                </div>
                
                <div className="mb-4">
                    <p className="text-center mb-2">lub</p>
                    <input
                        type="text"
                        value={joinGameId}
                        onChange={(e) => setJoinGameId(e.target.value)}
                        placeholder="Wpisz ID gry"
                        className="w-full bg-gray-800 text-white p-2 rounded mb-4"
                    />
                    <button 
                        onClick={() => onJoinGame(joinGameId)}
                        className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded"
                        disabled={!joinGameId}
                    >
                        Dołącz do gry
                    </button>
                </div>
            </div>
        </div>
    );
};

export default GameControls; 