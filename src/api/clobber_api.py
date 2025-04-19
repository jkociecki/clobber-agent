from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from clobber.clobber import Clobber
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


def initialize_game() -> Clobber:
    game = Clobber(6, 6)
    game.current_player = Piece.BLACK
    return game


async def get_or_create_game(game_id: str):
    game_data_key = f"game:{game_id}"
    clobber_game = in_memory_storage.get(game_data_key)
    if clobber_game:
        return clobber_game
    else:
        clobber_game = initialize_game()
        in_memory_storage[game_data_key] = clobber_game
        return clobber_game


def format_legal_moves(moves):
    formatted_moves = []
    for move in moves:
        from_pos = move.from_pos
        to_pos = move.to_pos

        def coords_to_algebraic(x, y):
            col = chr(ord('a') + x)
            row = str(6 - y)
            return col + row

        formatted_move = {
            "from": coords_to_algebraic(from_pos[0], from_pos[1]),
            "to": coords_to_algebraic(to_pos[0], to_pos[1])
        }
        formatted_moves.append(formatted_move)

    return formatted_moves


async def update_game_state(game_id: str, clobber_game):
    board = clobber_game.get_board()
    current_turn = "black" if clobber_game.current_player == Piece.BLACK else "white"
    legal_moves = format_legal_moves(clobber_game.get_legal_moves())
    is_terminal = clobber_game.is_terminal()

    if game_id in game_rooms:
        game_rooms[game_id]["current_turn"] = current_turn

    if game_id in game_rooms:
        for role, conn in game_rooms[game_id].items():
            if role != "current_turn" and conn:
                try:
                    game_state = {
                        "board": [[piece.value for piece in row] for row in board],
                        "turn": current_turn,
                        "legalMoves": legal_moves,
                        "isTerminal": is_terminal,
                        "status": "move made"
                    }
                    await conn.send_text(json.dumps(game_state))
                except Exception as e:
                    print(f"Error sending update to {role} player: {e}")


def parse_move(move_data):
    from_pos = move_data.get("from")
    to_pos = move_data.get("to")

    if not from_pos or not to_pos:
        return None

    def algebraic_to_coords(algebraic):
        col = ord(algebraic[0]) - ord('a')
        row = 5 - (int(algebraic[1]) - 1)
        return (col, row)

    from_coords = algebraic_to_coords(from_pos)
    to_coords = algebraic_to_coords(to_pos)

    return Move(from_coords, to_coords)


@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await websocket.accept()

    if game_id not in game_rooms:
        game_rooms[game_id] = {"black": None, "white": None, "current_turn": "black"}

    player_color = None
    if game_rooms[game_id]["black"] is None:
        game_rooms[game_id]["black"] = websocket
        player_color = "black"
    elif game_rooms[game_id]["white"] is None:
        game_rooms[game_id]["white"] = websocket
        player_color = "white"
    else:
        await websocket.send_text(json.dumps({"error": "Game room is full"}))
        await websocket.close()
        return

    active_connections[websocket] = {"game_id": game_id, "color": player_color}

    try:
        clobber_game = await get_or_create_game(game_id)
        current_turn = game_rooms[game_id]["current_turn"]
        clobber_game.current_player = Piece.BLACK if current_turn == "black" else Piece.WHITE
        legal_moves = format_legal_moves(clobber_game.get_legal_moves())
        board = clobber_game.get_board()

        await websocket.send_text(json.dumps({
            "board": [[piece.value for piece in row] for row in board],
            "turn": current_turn,
            "color": player_color,
            "legalMoves": legal_moves,
            "isTerminal": clobber_game.is_terminal()
        }))

        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message['action'] == 'get_board':
                clobber_game = await get_or_create_game(game_id)
                current_turn = "black" if clobber_game.current_player == Piece.BLACK else "white"
                legal_moves = format_legal_moves(clobber_game.get_legal_moves())
                board = clobber_game.get_board()

                await websocket.send_text(json.dumps({
                    "board": [[piece.value for piece in row] for row in board],
                    "turn": current_turn,
                    "legalMoves": legal_moves,
                    "isTerminal": clobber_game.is_terminal()
                }))

            elif message['action'] == 'make_move':
                clobber_game = await get_or_create_game(game_id)
                current_turn = "black" if clobber_game.current_player == Piece.BLACK else "white"

                player_piece = Piece.BLACK if player_color == "black" else Piece.WHITE

                if clobber_game.current_player == player_piece:
                    move_data = message.get("move")
                    move = parse_move(move_data)

                    if not move:
                        await websocket.send_text(json.dumps({
                            "error": "Invalid move format",
                            "board": [[piece.value for piece in row] for row in clobber_game.get_board()],
                            "turn": current_turn
                        }))
                        continue

                    legal_moves = clobber_game.get_legal_moves()
                    is_legal = False

                    for legal_move in legal_moves:
                        if legal_move.from_pos == move.from_pos and legal_move.to_pos == move.to_pos:
                            is_legal = True
                            move = legal_move
                            break

                    if is_legal:
                        clobber_game.make_move(move)
                        await update_game_state(game_id, clobber_game)
                    else:
                        await websocket.send_text(json.dumps({
                            "error": "Illegal move",
                            "board": [[piece.value for piece in row] for row in clobber_game.get_board()],
                            "turn": current_turn
                        }))
                else:
                    await websocket.send_text(json.dumps({
                        "error": "Not your turn",
                        "board": [[piece.value for piece in row] for row in clobber_game.get_board()],
                        "turn": current_turn
                    }))

            elif message['action'] == 'join_game':
                opponent_color = "black" if player_color == "white" else "white"
                opponent_socket = game_rooms[game_id].get(opponent_color)

                if opponent_socket:
                    await opponent_socket.send_text(json.dumps({
                        "status": f"Player {player_color} joined the game",
                        "opponent_joined": True
                    }))

    except WebSocketDisconnect:
        if websocket in active_connections:
            game_info = active_connections[websocket]
            if game_info["game_id"] in game_rooms:
                game_rooms[game_info["game_id"]][game_info["color"]] = None

                opponent_color = "black" if player_color == "white" else "white"
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
    return {"message": "Clobber API is running"} 
