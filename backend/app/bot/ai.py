"""FSM Bot AI for Stick Clash.
Implements distinct Easy, Normal, and Hard behaviors with smart platform navigation.
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
        self.pulse_timer = 0.0
        self.jump_pulse = 0
        self.attack_pulse = 0

        # Reaction intervals by difficulty
        if self.difficulty == "easy":
            self.reaction_interval = 0.36
            self.block_chance = 0.05
            self.parry_chance = 0.0
            self.combo_aggression = 0.2
            self.special_chance = 0.10
        elif self.difficulty == "hard":
            self.reaction_interval = 0.05
            self.block_chance = 0.85
            self.parry_chance = 0.80
            self.combo_aggression = 0.95
            self.special_chance = 0.90
        else:
            # Normal
            self.reaction_interval = 0.16
            self.block_chance = 0.40
            self.parry_chance = 0.25
            self.combo_aggression = 0.60
            self.special_chance = 0.50

    def decide_inputs(
        self,
        dt: float,
        self_player: Any,
        other_players: List[Any],
        pickups: List[Any],
    ) -> int:
        # Decrement pulse timers
        if self.jump_pulse > 0:
            self.jump_pulse -= 1
        if self.attack_pulse > 0:
            self.attack_pulse -= 1

        self.decision_timer -= dt
        if self.decision_timer > 0.0:
            # Maintain movement bits while clearing pulsed action bits
            current = self.cached_input
            if self.jump_pulse == 0:
                current &= ~InputBitmask.UP
            if self.attack_pulse == 0:
                current &= ~(InputBitmask.LIGHT | InputBitmask.HEAVY | InputBitmask.SPECIAL | InputBitmask.DASH)
            return current

        self.decision_timer = self.reaction_interval + random.uniform(-0.02, 0.02)

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

        # 1. Rage activation when ready (Normal & Hard)
        if self_player.combat.power >= 100.0:
            if self.difficulty == "hard":
                bitmask |= InputBitmask.RAGE
            elif self.difficulty == "normal" and random.random() < 0.65:
                bitmask |= InputBitmask.RAGE

        # 2. Defensive block / parry on incoming attacks
        is_target_attacking = target.combat.current_action in ["light1", "light2", "light3", "heavy", "slam", "dash_attack"]
        if is_target_attacking and dist < 140.0:
            if random.random() < self.block_chance:
                bitmask |= InputBitmask.BLOCK
                self.cached_input = bitmask
                return bitmask

        # 3. Special ability check
        if self_player.combat.power >= 40.0 and dist < 340.0 and self_player.combat.special_cooldown_timer <= 0.0:
            if random.random() < self.special_chance:
                bitmask |= InputBitmask.SPECIAL
                self.attack_pulse = 2
                self.cached_input = bitmask
                return bitmask

        # 4. Weapon / Crate collection (High priority on Hard and Normal)
        if not self_player.combat.held_weapon_type and pickups and self.difficulty in ["normal", "hard"]:
            closest_pickup = min(
                pickups,
                key=lambda p: math.hypot(p.x - self_player.physics.x, p.y - self_player.physics.y),
            )
            p_dist = math.hypot(closest_pickup.x - self_player.physics.x, closest_pickup.y - self_player.physics.y)
            if p_dist < 80.0:
                if closest_pickup.x > self_player.physics.x:
                    bitmask |= InputBitmask.RIGHT
                else:
                    bitmask |= InputBitmask.LEFT
                if p_dist < 45.0:
                    bitmask |= InputBitmask.GRAB
                    self.attack_pulse = 2
                self.cached_input = bitmask
                return bitmask

        # 5. Smart Platform Navigation & Movement
        if dist > 75.0:
            # Move towards target
            if dx > 15:
                bitmask |= InputBitmask.RIGHT
            elif dx < -15:
                bitmask |= InputBitmask.LEFT

            # Vertical tier navigation
            if dy < -50:
                # Target is above: Jump / Double Jump
                if self_player.physics.is_grounded or self_player.physics.jump_count < self_player.physics.max_jumps:
                    if random.random() < (0.9 if self.difficulty == "hard" else 0.7):
                        bitmask |= InputBitmask.UP
                        self.jump_pulse = 2  # Pulse for 2 frames
            elif dy > 70:
                # Target is below: Drop through thin platform
                if self_player.physics.is_grounded and random.random() < 0.6:
                    bitmask |= InputBitmask.DOWN

            # Dash to close distance or engage (Hard and Normal)
            if dist > 180.0 and self_player.combat.dash_cooldown_timer <= 0.0:
                if self.difficulty == "hard" and random.random() < 0.75:
                    bitmask |= InputBitmask.DASH
                    self.attack_pulse = 2
                elif self.difficulty == "normal" and random.random() < 0.35:
                    bitmask |= InputBitmask.DASH
                    self.attack_pulse = 2

        else:
            # Within close combat strike range!
            # Face enemy directly
            if dx > 4:
                bitmask |= InputBitmask.RIGHT
            elif dx < -4:
                bitmask |= InputBitmask.LEFT

            atk_roll = random.random()

            if self.difficulty == "hard":
                # Hard AI: Smart mix of combos, charged heavies, throws and slams
                if not self_player.physics.is_grounded:
                    # In air: down slam or air slash
                    if dy > 20:
                        bitmask |= (InputBitmask.DOWN | InputBitmask.LIGHT)
                    else:
                        bitmask |= InputBitmask.LIGHT
                elif target.combat.is_blocking:
                    # Target is blocking: use unblockable Throw!
                    bitmask |= InputBitmask.GRAB
                elif atk_roll < 0.55:
                    bitmask |= InputBitmask.LIGHT  # Fast combo
                elif atk_roll < 0.85:
                    bitmask |= InputBitmask.HEAVY  # Heavy strike
                else:
                    bitmask |= InputBitmask.GRAB
                self.attack_pulse = 2

            elif self.difficulty == "normal":
                # Normal AI: balanced attack mix
                if atk_roll < 0.65:
                    bitmask |= InputBitmask.LIGHT
                elif atk_roll < 0.88:
                    bitmask |= InputBitmask.HEAVY
                else:
                    bitmask |= InputBitmask.GRAB
                self.attack_pulse = 2

            else:
                # Easy AI: slower, single light attack, pauses between swings
                if atk_roll < 0.45:
                    bitmask |= InputBitmask.LIGHT
                    self.attack_pulse = 1
                elif atk_roll < 0.60:
                    bitmask |= InputBitmask.HEAVY
                    self.attack_pulse = 1

        self.cached_input = bitmask
        return bitmask
