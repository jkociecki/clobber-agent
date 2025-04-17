from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
from game_session import GameSession
import uvicorn
import uuid


app = FastAPI(title="Clobber Game API")
active_games: Dict[str, GameSession]


@app.post("/games")
async def create_game(request):
    print(request)


if __name__ == '__main__':
    uvicorn.run('clober_api:app', host='0.0.0.0', port=8000, reload=True)