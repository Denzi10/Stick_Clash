"""Free-for-All Mode (2 to 4 players, 5 min or 15 kills target)."""

from typing import Dict, List, Optional, Any
from .base_mode import BaseMode
from ..models.schemas import GameMode


class FreeForAllMode(BaseMode):
    def __init__(self, time_limit_secs: float = 300.0, target_kills: int = 15):
        super().__init__(GameMode.FFA, time_limit_secs, target_kills)
        self.is_sudden_death: bool = False

    def update(self, dt: float, active_players: list) -> None:
        if self.is_game_over:
            return

        self.time_remaining -= dt

        # Check if anyone hit target kills
        for p in active_players:
            kills = self.player_kills.get(p.id, 0)
            if kills >= self.target_kills:
                self.is_game_over = True
                self.winner_id = p.id
                return

        # Time limit expired
        if self.time_remaining <= 0.0:
            if not active_players:
                self.is_game_over = True
                return

            sorted_players = sorted(
                active_players, key=lambda p: self.player_kills.get(p.id, 0), reverse=True
            )
            top_kills = self.player_kills.get(sorted_players[0].id, 0)
            second_kills = (
                self.player_kills.get(sorted_players[1].id, 0)
                if len(sorted_players) > 1
                else -1
            )

            if top_kills > second_kills:
                self.is_game_over = True
                self.winner_id = sorted_players[0].id
            else:
                self.is_sudden_death = True

    def get_objective_info(self) -> Dict[str, Any]:
        return {
            "player_kills": self.player_kills,
            "target_kills": self.target_kills,
            "is_sudden_death": self.is_sudden_death,
            "target": f"First to {self.target_kills} Kills",
        }
