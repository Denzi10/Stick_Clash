"""Gauntlet (Continuous) Mode for Stick Clash.
Chains levels with objectives, upgrades draft, AI enemies and Stone Golem boss.
"""

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from .base_mode import BaseMode
from ..models.schemas import GameMode, UpgradeOffer


@dataclass
class UpgradeDef:
    id: str
    name: str
    description: str
    stat_key: str
    value: float
    cap: int


UPGRADES_POOL: List[UpgradeDef] = [
    UpgradeDef("heavy_hitter", "Heavy Hitter", "+10% damage", "damage_mult", 0.10, 3),
    UpgradeDef("thick_skin", "Thick Skin", "+15 max health", "max_health", 15.0, 3),
    UpgradeDef("quick_feet", "Quick Feet", "+8% move speed", "speed", 0.08, 3),
    UpgradeDef("power_surge", "Power Surge", "+20% power gain", "power_gain", 0.20, 3),
    UpgradeDef("second_wind", "Second Wind", "Survive lethal blow once per level", "second_wind", 1.0, 1),
    UpgradeDef("vampiric", "Vampiric", "Heal 5% of damage dealt", "lifesteal", 0.05, 2),
    UpgradeDef("long_arm", "Long Arm", "+10% attack range", "range", 0.10, 2),
    UpgradeDef("lucky_crates", "Lucky Crates", "Higher item spawn rarity", "luck", 1.0, 2),
    UpgradeDef("dash_master", "Dash Master", "Dash cooldown reduced by 20%", "dash_cdr", 0.20, 2),
    UpgradeDef("iron_guard", "Iron Guard", "+20 guard meter", "max_guard", 20.0, 2),
    UpgradeDef("elemental_touch", "Elemental Touch", "10% chance to burn on hit", "burn_chance", 0.10, 2),
    UpgradeDef("magnet_hands", "Magnet Hands", "Auto-collect items within 150 px", "magnet", 1.0, 1),
]


class GauntletMode(BaseMode):
    def __init__(
        self,
        total_time_limit_secs: float = 600.0,
        total_kill_target: int = 50,
        variant: str = "versus",  # "versus" or "co-op"
    ):
        super().__init__(GameMode.GAUNTLET, total_time_limit_secs, total_kill_target)
        self.variant = variant
        self.total_kills_count = 0
        self.current_level = 1
        self.level_state = "countdown"  # countdown, active, level_results, upgrade_pick
        self.countdown_timer = 3.0
        self.results_timer = 2.5
        self.upgrade_timer = 5.0
        self.needs_level_reset = False
        self.just_completed_level = False
        self.level_winner_id: Optional[str] = None

        # Level objective
        self.current_objective = "kill_count"
        self.level_time_limit = 120.0
        self.level_time_remaining = 120.0
        self.level_kill_target = 10
        self.level_kills: Dict[str, int] = {}

        # King of the hill objective
        self.hill_x = 640.0
        self.hill_y = 350.0
        self.hill_radius = 120.0
        self.hill_hold_time: Dict[str, float] = {}

        # Co-op shared lives
        self.shared_lives = 6

        # Boss info
        self.boss_active = False
        self.boss_health = 0.0
        self.boss_max_health = 0.0
        self.boss_phase = 1

        # Upgrades applied per player
        self.player_upgrades: Dict[str, Dict[str, int]] = {}
        self.pending_offers: Dict[str, List[UpgradeOffer]] = {}

        self.setup_level()

    def setup_level(self) -> None:
        self.level_state = "countdown"
        self.countdown_timer = 3.0
        self.level_kills.clear()
        self.hill_hold_time.clear()

        # Every 5th level is Boss level
        if self.current_level % 5 == 0:
            self.current_objective = "boss"
            self.level_time_limit = 240.0
            self.boss_active = True
            self.boss_max_health = 1200.0
            self.boss_health = self.boss_max_health
            self.boss_phase = 1
        else:
            self.boss_active = False
            objectives = ["kill_count", "timed_score", "last_standing", "king_of_the_hill"]
            if self.variant == "co-op":
                objectives.append("survival")
            self.current_objective = random.choice(objectives)

            if self.current_objective == "kill_count":
                self.level_time_limit = 120.0
                self.level_kill_target = 10
            elif self.current_objective == "timed_score":
                self.level_time_limit = 90.0
            elif self.current_objective == "last_standing":
                self.level_time_limit = 120.0
            elif self.current_objective == "king_of_the_hill":
                self.level_time_limit = 150.0
            elif self.current_objective == "survival":
                self.level_time_limit = 180.0

        self.level_time_remaining = self.level_time_limit

    def update(self, dt: float, active_players: list) -> None:
        if self.is_game_over:
            return

        self.time_remaining -= dt
        if self.time_remaining <= 0.0 or self.total_kills_count >= self.target_kills:
            self.is_game_over = True
            # Determine winner by total score
            if active_players:
                self.winner_id = max(
                    active_players, key=lambda p: self.player_scores.get(p.id, 0)
                ).id
            return

        # State machine
        if self.level_state == "countdown":
            self.countdown_timer -= dt
            if self.countdown_timer <= 0.0:
                self.level_state = "active"

        elif self.level_state == "active":
            self.level_time_remaining -= dt

            # King of the hill tracking
            if self.current_objective == "king_of_the_hill":
                for p in active_players:
                    dx = p.physics.x - self.hill_x
                    dy = p.physics.y - self.hill_y
                    if (dx * dx + dy * dy) <= (self.hill_radius * self.hill_radius):
                        self.hill_hold_time[p.id] = self.hill_hold_time.get(p.id, 0.0) + dt
                        if self.hill_hold_time[p.id] >= 45.0:
                            self.complete_level(p.id, active_players)
                            return

            # Check level completion - if an opponent dies in gauntlet level
            alive_players = [p for p in active_players if p.combat.health > 0.0]
            if len(alive_players) <= 1:
                winner = alive_players[0].id if alive_players else None
                self.complete_level(winner, active_players)
                return

            if self.current_objective == "boss" and self.boss_health <= 0.0:
                self.complete_level(None, active_players)
                return

            if self.level_time_remaining <= 0.0:
                self.complete_level(None, active_players)

        elif self.level_state == "level_results":
            self.results_timer -= dt
            if self.results_timer <= 0.0:
                self.generate_upgrade_offers(active_players)
                self.level_state = "upgrade_pick"
                self.upgrade_timer = 5.0

        elif self.level_state == "upgrade_pick":
            self.upgrade_timer -= dt
            if self.upgrade_timer <= 0.0 or len(self.pending_offers) == 0:
                # Advance to next level
                self.current_level += 1
                self.setup_level()
                self.needs_level_reset = True

    def complete_level(self, winner_player_id: Optional[str], active_players: list) -> None:
        self.level_state = "level_results"
        self.results_timer = 2.5
        self.just_completed_level = True
        self.level_winner_id = winner_player_id
        if winner_player_id:
            self.player_scores[winner_player_id] = (
                self.player_scores.get(winner_player_id, 0) + 200
            )

    def generate_upgrade_offers(self, active_players: list) -> None:
        self.pending_offers.clear()
        for p in active_players:
            if p.is_bot:
                continue
            curr_upgrades = self.player_upgrades.get(p.id, {})
            # Pick 3 random eligible upgrades
            available = [u for u in UPGRADES_POOL if curr_upgrades.get(u.id, 0) < u.cap]
            if len(available) < 3:
                available = UPGRADES_POOL
            sampled = random.sample(available, min(3, len(available)))

            offers = [
                UpgradeOffer(
                    id=u.id,
                    name=u.name,
                    description=u.description,
                    stat_key=u.stat_key,
                    value=u.value,
                    current_stacks=curr_upgrades.get(u.id, 0),
                    max_stacks=u.cap,
                )
                for u in sampled
            ]
            self.pending_offers[p.id] = offers

    def select_upgrade(self, player_id: str, upgrade_id: str) -> bool:
        if player_id not in self.pending_offers:
            return False

        if player_id not in self.player_upgrades:
            self.player_upgrades[player_id] = {}

        self.player_upgrades[player_id][upgrade_id] = (
            self.player_upgrades[player_id].get(upgrade_id, 0) + 1
        )
        del self.pending_offers[player_id]
        return True

    def get_objective_info(self) -> Dict[str, Any]:
        return {
            "level": self.current_level,
            "level_state": self.level_state,
            "objective": self.current_objective,
            "level_time_remaining": round(self.level_time_remaining, 1),
            "total_kills": self.total_kills_count,
            "target_kills": self.target_kills,
            "boss_active": self.boss_active,
            "boss_health": self.boss_health,
            "boss_max_health": self.boss_max_health,
            "hill_hold_time": {k: round(v, 1) for k, v in self.hill_hold_time.items()},
        }
