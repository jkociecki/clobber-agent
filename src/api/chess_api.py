from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from chess.chess_state import Chess
from general.enums import Piece
from general.move import Move
import json
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

in_memory_storage = {}
active_connections = {}
game_rooms = {}


def initialize_game() -> Chess:
    return Chess()


async def get_or_create_game(game_id: str):
    game_data_key = f"game:{game_id}"

    chess_game = in_memory_storage.get(game_data_key)

    if chess_game:
        return chess_game
    else:
        chess_game = initialize_game()
        in_memory_storage[game_data_key] = chess_game
        return chess_game


def format_legal_moves(moves):
    formatted_moves = []
    for move in moves:
        from_pos = move.from_pos
        to_pos = move.to_pos
        promotion = move.prom if move.prom else None

        from_algebraic = chr(from_pos[1] + ord('a')) + str(8 - from_pos[0])
        to_algebraic = chr(to_pos[1] + ord('a')) + str(8 - from_pos[0])

        formatted_move = {
            "from": from_algebraic,
            "to": to_algebraic,
            "promotion": promotion
        }
        formatted_moves.append(formatted_move)

    return formatted_moves


async def update_game_state(game_id: str, chess_game):
    fen_string = chess_game.get_fen()
    current_turn = "white" if chess_game.current_player == Piece.WHITE else "black"
    print(f"Current turn: {current_turn}")
    game_state = chess_game.get_game_state()
    legal_moves = format_legal_moves(chess_game.get_legal_moves())

    if game_id in game_rooms:
        for role, conn in game_rooms[game_id].items():
            if role != "current_turn" and conn:
                try:
                    await conn.send_text(json.dumps({
                        "fen": fen_string,
                        "turn": current_turn,
                        "gameState": game_state,
                        "legalMoves": legal_moves,
                        "status": "move made"
                    }))
                except Exception as e:
                    print(f"Error sending update to {role} player: {e}")


def parse_move(move_data):
    from_algebraic = move_data.get("from")
    to_algebraic = move_data.get("to")
    promotion = move_data.get("promotion")

    if not from_algebraic or not to_algebraic:
        return None

    from_col = ord(from_algebraic[0]) - ord('a')
    from_row = 8 - int(from_algebraic[1])

    to_col = ord(to_algebraic[0]) - ord('a')
    to_row = 8 - int(to_algebraic[1])

    return Move((from_row, from_col), (to_row, to_col), promotion)


@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await websocket.accept()
    print(f"Client connected to game: {game_id}")

    if game_id not in game_rooms:
        game_rooms[game_id] = {"white": None, "black": None, "current_turn": "white"}

    player_color = None
    if game_rooms[game_id]["white"] is None:
        game_rooms[game_id]["white"] = websocket
        player_color = "white"
    elif game_rooms[game_id]["black"] is None:
        game_rooms[game_id]["black"] = websocket
        player_color = "black"
    else:
        await websocket.send_text(json.dumps({"error": "Game room is full"}))
        await websocket.close()
        return

    print(f"Player assigned color: {player_color} in game: {game_id}")
    active_connections[websocket] = {"game_id": game_id, "color": player_color}

    try:
        chess_game = await get_or_create_game(game_id)
        current_turn = "white" if chess_game.current_player == Piece.WHITE else "black"
        legal_moves = format_legal_moves(chess_game.get_legal_moves())
        game_state = chess_game.get_game_state()

        await websocket.send_text(json.dumps({
            "fen": chess_game.get_fen(),
            "turn": current_turn,
            "color": player_color,
            "gameState": game_state,
            "legalMoves": legal_moves
        }))

        while True:
            data = await websocket.receive_text()
            print(f"Received data from {player_color}: {data}")
            message = json.loads(data)

            if message['action'] == 'get_board':
                chess_game = await get_or_create_game(game_id)
                current_turn = "white" if chess_game.current_player == Piece.WHITE else "black"
                legal_moves = format_legal_moves(chess_game.get_legal_moves())
                game_state = chess_game.get_game_state()

                await websocket.send_text(json.dumps({
                    "fen": chess_game.get_fen(),
                    "turn": current_turn,
                    "gameState": game_state,
                    "legalMoves": legal_moves
                }))

            elif message['action'] == 'make_move':
                chess_game = await get_or_create_game(game_id)
                current_turn = "white" if chess_game.current_player == Piece.WHITE else "black"

                if current_turn == player_color:
                    move_data = message.get("move")
                    move = parse_move(move_data)

                    if not move:
                        await websocket.send_text(json.dumps({
                            "error": "Invalid move format",
                            "fen": chess_game.get_fen(),
                            "turn": current_turn
                        }))
                        continue

                    legal_moves = chess_game.get_legal_moves()
                    is_legal = False

                    for legal_move in legal_moves:
                        if legal_move.from_pos == move.from_pos and legal_move.to_pos == move.to_pos:
                            if move.prom == legal_move.prom:
                                is_legal = True
                                move = legal_move
                                break

                    if is_legal:
                        chess_game.make_move(move)
                        await update_game_state(game_id, chess_game)
                    else:
                        await websocket.send_text(json.dumps({
                            "error": "Illegal move",
                            "fen": chess_game.get_fen(),
                            "turn": current_turn
                        }))
                else:
                    await websocket.send_text(json.dumps({
                        "error": "Not your turn",
                        "fen": chess_game.get_fen(),
                        "turn": current_turn
                    }))

            elif message['action'] == 'join_game':
                opponent_color = "white" if player_color == "black" else "black"
                opponent_socket = game_rooms[game_id].get(opponent_color)

                if opponent_socket:
                    await opponent_socket.send_text(json.dumps({
                        "status": f"Player {player_color} joined the game",
                        "opponent_joined": True
                    }))

    except WebSocketDisconnect:
        print(f"Client disconnected from game: {game_id}, color: {player_color}")
        if websocket in active_connections:
            game_info = active_connections[websocket]
            if game_info["game_id"] in game_rooms:
                game_rooms[game_info["game_id"]][game_info["color"]] = None

                opponent_color = "white" if player_color == "black" else "black"
                opponent_socket = game_rooms[game_id].get(opponent_color)

                if opponent_socket:
                    try:
                        await opponent_socket.send_text(json.dumps({
                            "status": f"Player {player_color} disconnected",
                            "opponent_disconnected": True
                        }))
                    except Exception:
                        pass

            del active_connections[websocket]
    except Exception as e:
        print(f"Error in WebSocket connection: {e}")
        if websocket in active_connections:
            game_info = active_connections[websocket]
            if game_info["game_id"] in game_rooms:
                game_rooms[game_info["game_id"]][game_info["color"]] = None
            del active_connections[websocket]


@app.get("/new_game/")
async def new_game():
    game_id = str(uuid.uuid4())
    await get_or_create_game(game_id)
    return JSONResponse(content={"game_id": game_id})


@app.get("/")
async def root():
    return {"message": "Chess API is running"}
