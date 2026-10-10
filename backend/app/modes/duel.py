"""Duel Mode (1v1, Best of 3 rounds, 90s round timer)."""

from typing import Dict, List, Optional, Any
from .base_mode import BaseMode
from ..models.schemas import GameMode


class DuelMode(BaseMode):
    def __init__(self, time_limit_secs: float = 90.0):
        super().__init__(GameMode.DUEL, time_limit_secs, target_kills=2)
        self.current_round: int = 1
        self.max_rounds: int = 3
        self.round_wins: Dict[str, int] = {}
        self.round_in_progress: bool = True
        self.round_break_timer: float = 0.0
        self.needs_round_reset: bool = False
        self.just_finished_round: bool = False
        self.last_round_winner: Optional[str] = None

    def update(self, dt: float, active_players: list) -> None:
        if self.is_game_over:
            return

        if self.round_break_timer > 0.0:
            self.round_break_timer -= dt
            if self.round_break_timer <= 0.0:
                self.round_in_progress = True
                self.time_remaining = self.time_limit
                self.needs_round_reset = True
            return

        if self.round_in_progress:
            self.time_remaining -= dt

            # Check if any player's health hit 0 or time ran out
            alive_players = [p for p in active_players if p.combat.health > 0.0]
            if len(alive_players) <= 1 or self.time_remaining <= 0.0:
                self.finish_round(alive_players, active_players)

    def finish_round(self, alive_players: list, all_players: list) -> None:
        self.round_in_progress = False
        self.round_break_timer = 2.5  # 2.5s pause before next round
        self.just_finished_round = True

        if len(alive_players) == 1:
            winner = alive_players[0].id
        elif len(all_players) == 2:
            # Time out: higher health wins
            p1, p2 = all_players[0], all_players[1]
            winner = p1.id if p1.combat.health > p2.combat.health else p2.id
        else:
            winner = None

        self.last_round_winner = winner

        if winner:
            self.round_wins[winner] = self.round_wins.get(winner, 0) + 1
            if self.round_wins[winner] >= 2:
                self.is_game_over = True
                self.winner_id = winner
                return

        self.current_round += 1
        if self.current_round > self.max_rounds:
            self.is_game_over = True
            # Highest wins
            if self.round_wins:
                self.winner_id = max(self.round_wins.items(), key=lambda x: x[1])[0]

    def get_objective_info(self) -> Dict[str, Any]:
        return {
            "round": self.current_round,
            "max_rounds": self.max_rounds,
            "round_wins": self.round_wins,
            "round_in_progress": self.round_in_progress,
            "round_break_timer": round(self.round_break_timer, 1),
            "target": "Best of 3 Rounds",
        }
