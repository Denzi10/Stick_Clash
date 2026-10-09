"""FSM Bot AI for Stick Clash.
Implements Easy, Normal, and Hard behavior with no hidden information.
"""

import math
import random
from typing import Dict, List, Optional, Tuple, Any
from ..models.schemas import InputBitmask, FighterClass


class BotAI:
    def __init__(self, bot_id: str, difficulty: str = "normal"):
        self.bot_id = bot_id
        self.difficulty = difficulty.lower()  # easy, normal, hard
        self.state = "idle"
        self.decision_timer = 0.0
        self.cached_input = 0
        self.reaction_interval = (
            0.35 if self.difficulty == "easy" else (0.20 if self.difficulty == "normal" else 0.08)
        )

    def decide_inputs(
        self,
        dt: float,
        self_player: Any,
        other_players: List[Any],
        pickups: List[Any],
    ) -> int:
        self.decision_timer -= dt
        if self.decision_timer > 0.0:
            return self.cached_input

        self.decision_timer = self.reaction_interval + random.uniform(-0.03, 0.03)

        bitmask = 0
        if not other_players:
            self.cached_input = 0
            return 0

        # Find closest hostile enemy
        hostiles = [p for p in other_players if p.team != self_player.team and p.combat.health > 0.0]
        if not hostiles:
            hostiles = [p for p in other_players if p.id != self_player.id and p.combat.health > 0.0]

        if not hostiles:
            self.cached_input = 0
            return 0

        target = min(
            hostiles,
            key=lambda p: math.hypot(p.physics.x - self_player.physics.x, p.physics.y - self_player.physics.y),
        )

        dx = target.physics.x - self_player.physics.x
        dy = target.physics.y - self_player.physics.y
        dist = math.hypot(dx, dy)

        # 1. Rage activation when ready
        if self_player.combat.power >= 100.0:
            if self.difficulty in ["normal", "hard"] or random.random() < 0.5:
                bitmask |= InputBitmask.RAGE

        # 2. Defensive block / parry on incoming attacks
        if target.combat.current_action in ["light1", "light2", "light3", "heavy", "slam"] and dist < 120.0:
            if self.difficulty == "hard":
                # High chance to parry or block
                if random.random() < 0.85:
                    bitmask |= InputBitmask.BLOCK
                    self.cached_input = bitmask
                    return bitmask
            elif self.difficulty == "normal" and random.random() < 0.50:
                bitmask |= InputBitmask.BLOCK
                self.cached_input = bitmask
                return bitmask

        # 3. Special ability check
        if self_player.combat.power >= 50.0 and dist < 300.0:
            if (self.difficulty == "hard" and random.random() < 0.7) or (self.difficulty == "normal" and random.random() < 0.4):
                bitmask |= InputBitmask.SPECIAL

        # 4. Movement: Chase target
        if dist > 85.0:
            if dx > 15:
                bitmask |= InputBitmask.RIGHT
            elif dx < -15:
                bitmask |= InputBitmask.LEFT

            # Jump if target is higher up
            if dy < -40 and (self_player.physics.is_grounded or random.random() < 0.3):
                bitmask |= InputBitmask.UP

            # Drop through platform if target is significantly below
            if dy > 60 and random.random() < 0.4:
                bitmask |= InputBitmask.DOWN

            # Dash to close gap
            if dist > 200.0 and self_player.combat.dash_cooldown_timer <= 0.0 and self.difficulty in ["normal", "hard"]:
                if random.random() < 0.5:
                    bitmask |= InputBitmask.DASH

        else:
            # Within attack range!
            # Face target
            if dx > 5:
                bitmask |= InputBitmask.RIGHT
            elif dx < -5:
                bitmask |= InputBitmask.LEFT

            # Choose attack
            atk_roll = random.random()
            if self.difficulty == "hard":
                if atk_roll < 0.45:
                    bitmask |= InputBitmask.LIGHT
                elif atk_roll < 0.70:
                    bitmask |= InputBitmask.HEAVY
                elif atk_roll < 0.85:
                    bitmask |= InputBitmask.GRAB
                else:
                    bitmask |= InputBitmask.DASH
            elif self.difficulty == "normal":
                if atk_roll < 0.60:
                    bitmask |= InputBitmask.LIGHT
                elif atk_roll < 0.85:
                    bitmask |= InputBitmask.HEAVY
                else:
                    bitmask |= InputBitmask.GRAB
            else:
                # Easy
                if atk_roll < 0.50:
                    bitmask |= InputBitmask.LIGHT
                elif atk_roll < 0.70:
                    bitmask |= InputBitmask.HEAVY

        # Pick up item if nearby
        if not self_player.combat.held_weapon_type and pickups:
            nearby_pickups = [p for p in pickups if math.hypot(p.x - self_player.physics.x, p.y - self_player.physics.y) < 60.0]
            if nearby_pickups and random.random() < 0.6:
                bitmask |= InputBitmask.GRAB

        self.cached_input = bitmask
        return bitmask
