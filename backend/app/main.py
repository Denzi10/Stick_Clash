"""Stick Clash - FastAPI Application & WebSocket Server."""

import asyncio
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .models.schemas import FighterClass, GameMode, RoomInfo
from .rooms import room_manager, GameRoom
from .simulation.classes import CLASS_STATS
from .simulation.arenas import build_arenas

app = FastAPI(title="Stick Clash Game Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateRoomRequest(BaseModel):
    mode: GameMode = GameMode.DUEL
    arena_id: str = "training_dojo"
    max_players: int = 4


@app.get("/api/health")
def health_check():
    return {"status": "ok", "game": "Stick Clash", "version": "1.0.0"}


@app.get("/api/classes")
def get_classes():
    return {
        cls.value: {
            "name": stats.class_name.value.capitalize(),
            "health": stats.health,
            "speed": stats.speed,
            "damage_mult": stats.damage_mult,
            "weight": stats.weight,
            "special_name": stats.special_name,
            "description": stats.description,
        }
        for cls, stats in CLASS_STATS.items()
    }


@app.get("/api/arenas")
def get_arenas():
    arenas = build_arenas()
    return {
        a.id: {
            "name": a.name,
            "theme": a.theme,
            "wrap": a.wrap_horizontal,
            "hazards_count": len(a.hazards),
        }
        for a in arenas.values()
    }


@app.get("/api/rooms")
def list_rooms():
    return room_manager.list_rooms()


@app.post("/api/rooms/create")
def create_room(req: CreateRoomRequest):
    room = room_manager.create_room(
        mode=req.mode, arena_id=req.arena_id, max_players=req.max_players
    )
    return {
        "room_code": room.room_code,
        "mode": room.mode_type,
        "arena_id": room.arena_id,
        "max_players": room.max_players,
    }


@app.get("/api/rooms/{code}")
def get_room_info(code: str):
    room = room_manager.get_room(code)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return {
        "room_code": room.room_code,
        "mode": room.mode_type,
        "arena_id": room.arena_id,
        "players_count": len(room.players),
        "max_players": room.max_players,
        "in_game": room.in_game,
    }


@app.websocket("/ws/{room_code}")
async def websocket_game_endpoint(websocket: WebSocket, room_code: str):
    await websocket.accept()
    room = room_manager.get_room(room_code)
    if not room:
        # Auto-create if doesn't exist
        room = room_manager.create_room(mode=GameMode.FFA, arena_id="training_dojo")
        room.room_code = room_code.upper()
        room_manager.rooms[room.room_code] = room

    player_id: Optional[str] = None

    try:
        while True:
            msg = await websocket.receive_json()
            mtype = msg.get("type")

            if mtype in ["join", "select_class"]:
                player_id = msg.get("player_id") or str(len(room.players) + 1)
                nickname = (msg.get("nickname") or f"Player {len(room.players) + 1}")[:16]
                f_class_str = msg.get("fighter_class", "brawler")
                f_class = FighterClass(f_class_str)
                team = int(msg.get("team", len(room.players) % 2))

                # Check if reconnecting or updating fighter class in lobby
                if player_id in room.players:
                    p = room.players[player_id]
                    p.connected = True
                    p.disconnected_at = None
                    p.is_bot = False
                    p.bot_ai = None
                    p.fighter_class = f_class
                    from .simulation.combat import CombatState
                    p.combat = CombatState(f_class)
                    p.team = team
                else:
                    room.add_player(player_id, nickname, f_class, team=team)

                room.connections[player_id] = websocket

                # Broadcast lobby update
                await broadcast_lobby(room)

            elif mtype == "set_mode" and player_id == room.host_id:
                new_mode_str = msg.get("mode", "duel")
                room.set_mode(new_mode_str)
                if "arena_id" in msg:
                    room.arena_id = msg["arena_id"]
                    room.arena_manager.set_arena(msg["arena_id"])
                await broadcast_lobby(room)

            elif mtype == "input" and player_id and player_id in room.players:
                bitmask = int(msg.get("bitmask", 0))
                seq = int(msg.get("seq", 0))
                p = room.players[player_id]
                p.latest_input_bitmask = bitmask
                p.input_sequence = seq

            elif mtype == "start_game" and player_id == room.host_id:
                if not room.in_game:
                    diff = msg.get("difficulty", "normal")
                    await room.start_game(default_bot_difficulty=diff)
                    for ws in room.connections.values():
                        await ws.send_json(
                            {
                                "type": "game_started",
                                "arena_id": room.arena_id,
                                "mode": room.mode_type,
                            }
                        )

            elif mtype == "add_bot" and player_id == room.host_id:
                if len(room.players) < room.max_players:
                    bot_id = f"bot_{len(room.players) + 1}"
                    diff = msg.get("difficulty", "normal")
                    b_class_str = msg.get("fighter_class", "brawler")
                    b_class = FighterClass(b_class_str)
                    team = int(msg.get("team", len(room.players) % 2))
                    room.add_player(
                        bot_id,
                        f"Bot {len(room.players) + 1}",
                        b_class,
                        team=team,
                        is_bot=True,
                        difficulty=diff,
                    )
                    await broadcast_lobby(room)

            elif mtype == "select_upgrade" and player_id and room.mode_type == GameMode.GAUNTLET:
                upgrade_id = msg.get("upgrade_id")
                if isinstance(room.game_mode, GauntletMode):
                    room.game_mode.select_upgrade(player_id, upgrade_id)

            elif mtype == "emote" and player_id:
                emote_id = msg.get("emote_id", "fight")
                for ws in room.connections.values():
                    await ws.send_json(
                        {"type": "emote", "player_id": player_id, "emote_id": emote_id}
                    )

    except WebSocketDisconnect:
        if player_id and player_id in room.connections:
            del room.connections[player_id]
        if player_id and player_id in room.players:
            p = room.players[player_id]
            p.connected = False
            import time
            p.disconnected_at = time.time()
        await broadcast_lobby(room)


async def broadcast_lobby(room: GameRoom) -> None:
    roster = [
        {
            "id": p.id,
            "nickname": p.nickname,
            "fighter_class": p.fighter_class.value,
            "team": p.team,
            "is_host": (p.id == room.host_id),
            "is_bot": p.is_bot,
            "difficulty": p.bot_difficulty,
            "connected": p.connected,
        }
        for p in room.players.values()
    ]
    payload = {
        "type": "lobby_update",
        "room_code": room.room_code,
        "mode": room.mode_type,
        "arena_id": room.arena_id,
        "in_game": room.in_game,
        "host_id": room.host_id,
        "players": roster,
    }
    for ws in list(room.connections.values()):
        try:
            await ws.send_json(payload)
        except Exception:
            pass


# Mount static build of frontend if exists
frontend_dist = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
)
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
