"""Base Game Mode Interface for Stick Clash."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
from ..models.schemas import GameMode


class BaseMode(ABC):
    def __init__(self, mode: GameMode, time_limit_secs: float, target_kills: int):
        self.mode = mode
        self.time_limit = time_limit_secs
        self.time_remaining = time_limit_secs
        self.target_kills = target_kills
        self.is_game_over = False
        self.winning_team: Optional[int] = None
        self.winner_id: Optional[str] = None
        self.player_scores: Dict[str, int] = {}
        self.player_kills: Dict[str, int] = {}
        self.player_deaths: Dict[str, int] = {}
        self.player_assists: Dict[str, int] = {}
        # Assist tracker: maps player_id -> dict of (damager_id -> timestamp)
        self.recent_damagers: Dict[str, Dict[str, float]] = {}

    def register_damage(self, attacker_id: str, target_id: str, damage: float, current_time: float) -> None:
        if target_id not in self.recent_damagers:
            self.recent_damagers[target_id] = {}
        self.recent_damagers[target_id][attacker_id] = current_time

    def process_kill(self, victim_id: str, killer_id: Optional[str], current_time: float) -> Tuple[Optional[str], Optional[str]]:
        """Processes a KO, credits kill to last damager within 5s, assist to second damager."""
        actual_killer = killer_id
        assist_id = None

        if victim_id in self.recent_damagers:
            recent = self.recent_damagers[victim_id]
            # Valid within previous 5 seconds
            valid_damagers = [
                (p, t) for p, t in recent.items() if (current_time - t) <= 5.0 and p != victim_id
            ]
            valid_damagers.sort(key=lambda x: x[1], reverse=True)

            if valid_damagers:
                actual_killer = valid_damagers[0][0]
                if len(valid_damagers) > 1:
                    assist_id = valid_damagers[1][0]
            del self.recent_damagers[victim_id]

        if actual_killer:
            self.player_kills[actual_killer] = self.player_kills.get(actual_killer, 0) + 1
            self.player_scores[actual_killer] = self.player_scores.get(actual_killer, 0) + 100
        else:
            # Self-KO or hazard death with no damager: -1 point
            self.player_scores[victim_id] = max(0, self.player_scores.get(victim_id, 0) - 25)

        if assist_id:
            self.player_assists[assist_id] = self.player_assists.get(assist_id, 0) + 1
            self.player_scores[assist_id] = self.player_scores.get(assist_id, 0) + 25

        self.player_deaths[victim_id] = self.player_deaths.get(victim_id, 0) + 1
        return actual_killer, assist_id

    @abstractmethod
    def update(self, dt: float, active_players: list) -> None:
        pass

    @abstractmethod
    def get_objective_info(self) -> Dict[str, Any]:
        pass
