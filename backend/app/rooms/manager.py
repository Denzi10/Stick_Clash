"""Room Manager and Matchmaking for Stick Clash."""

import random
from typing import Dict, List, Optional
from ..config import ROOM_CODE_ALPHABET, ROOM_CODE_LENGTH
from ..models.schemas import GameMode, RoomInfo
from .room import GameRoom


class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, GameRoom] = {}

    def generate_code(self) -> str:
        for _ in range(100):
            code = "".join(random.choice(ROOM_CODE_ALPHABET) for _ in range(ROOM_CODE_LENGTH))
            if code not in self.rooms:
                return code
        # Fallback
        import uuid
        return str(uuid.uuid4())[:ROOM_CODE_LENGTH].upper()

    def create_room(
        self,
        mode: GameMode = GameMode.DUEL,
        arena_id: str = "training_dojo",
        max_players: int = 4,
    ) -> GameRoom:
        code = self.generate_code()
        room = GameRoom(code, mode=mode, arena_id=arena_id, max_players=max_players)
        self.rooms[code] = room
        return room

    def get_room(self, code: str) -> Optional[GameRoom]:
        return self.rooms.get(code.upper().strip())

    def quick_match(self) -> GameRoom:
        """Finds an existing non-full room that has not started yet, or creates a new FFA room."""
        for room in self.rooms.values():
            if not room.in_game and len(room.players) < room.max_players:
                return room
        return self.create_room(mode=GameMode.FFA, arena_id="training_dojo", max_players=4)

    def remove_room(self, code: str) -> None:
        if code in self.rooms:
            room = self.rooms[code]
            if room.loop_task and not room.loop_task.done():
                room.loop_task.cancel()
            del self.rooms[code]

    def list_rooms(self) -> List[RoomInfo]:
        info_list = []
        for r in self.rooms.values():
            host_name = "Host"
            if r.host_id and r.host_id in r.players:
                host_name = r.players[r.host_id].nickname
            info_list.append(
                RoomInfo(
                    room_code=r.room_code,
                    mode=r.mode_type,
                    arena_id=r.arena_id,
                    players_count=len(r.players),
                    max_players=r.max_players,
                    in_game=r.in_game,
                    host_nickname=host_name,
                    target_score=r.game_mode.target_kills,
                    time_limit_secs=int(r.game_mode.time_limit),
                )
            )
        return info_list


room_manager = RoomManager()
