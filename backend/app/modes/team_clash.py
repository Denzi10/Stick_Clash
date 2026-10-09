"""Team Clash Mode (2v2, 5 min or 20 kills target)."""

from typing import Dict, List, Optional, Any
from .base_mode import BaseMode
from ..models.schemas import GameMode


class TeamClashMode(BaseMode):
    def __init__(self, time_limit_secs: float = 300.0, target_kills: int = 20):
        super().__init__(GameMode.TEAM_CLASH, time_limit_secs, target_kills)
        self.team_kills: Dict[int, int] = {0: 0, 1: 0}
        self.is_sudden_death: bool = False

    def update(self, dt: float, active_players: list) -> None:
        if self.is_game_over:
            return

        self.time_remaining -= dt

        # Recalculate team kills
        t0_kills = sum(self.player_kills.get(p.id, 0) for p in active_players if p.team == 0)
        t1_kills = sum(self.player_kills.get(p.id, 0) for p in active_players if p.team == 1)
        self.team_kills[0] = t0_kills
        self.team_kills[1] = t1_kills

        # Target kill win check
        if t0_kills >= self.target_kills:
            self.is_game_over = True
            self.winning_team = 0
            return
        elif t1_kills >= self.target_kills:
            self.is_game_over = True
            self.winning_team = 1
            return

        # Time limit check
        if self.time_remaining <= 0.0:
            if t0_kills > t1_kills:
                self.is_game_over = True
                self.winning_team = 0
            elif t1_kills > t0_kills:
                self.is_game_over = True
                self.winning_team = 1
            else:
                # Sudden death: next kill wins
                self.is_sudden_death = True

    def get_objective_info(self) -> Dict[str, Any]:
        return {
            "team_kills": self.team_kills,
            "target_kills": self.target_kills,
            "is_sudden_death": self.is_sudden_death,
            "target": f"First to {self.target_kills} Kills",
        }
