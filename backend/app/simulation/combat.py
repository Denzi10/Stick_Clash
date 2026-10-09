"""Core Combat System for Stick Clash.
Implements moves, frame data, hitboxes, knockback, hit-stop, parry, block, and combos.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from ..config import (
    BLOCK_DAMAGE_REDUCTION,
    BLOCK_KNOCKBACK_REDUCTION,
    GUARD_BREAK_STUN,
    PARRY_WINDOW_SECS,
    PARRY_STUN_DURATION,
    PARRY_POWER_GAIN,
    SPECIAL_POWER_COST,
    SPECIAL_POWER_COST_RAGE,
    RAGE_POWER_COST,
    RAGE_DURATION,
    RAGE_DAMAGE_BUFF,
    RAGE_SPEED_BUFF,
    RAGE_HEALTH_REGEN,
    MAX_POWER,
    TICK_DT,
)
from ..models.schemas import StatusType, FighterClass, WeaponType
from .physics import AABB, PhysicsBody
from .statuses import StatusManager
from .classes import CLASS_STATS


@dataclass
class MoveFrameData:
    name: str
    startup_frames: int
    active_frames: int
    recovery_frames: int
    damage: float
    base_knockback: float
    hitbox_offset_x: float
    hitbox_offset_y: float
    hitbox_w: float
    hitbox_h: float
    is_downward_spike: bool = False
    is_unblockable: bool = False


MOVE_TABLE: Dict[str, MoveFrameData] = {
    "light1": MoveFrameData("light1", 4, 3, 8, 5.0, 120.0, 35.0, -45.0, 50.0, 40.0),
    "light2": MoveFrameData("light2", 4, 3, 8, 5.0, 120.0, 35.0, -45.0, 50.0, 40.0),
    "light3": MoveFrameData("light3", 6, 4, 10, 8.0, 260.0, 40.0, -45.0, 60.0, 45.0),
    "heavy": MoveFrameData("heavy", 14, 5, 18, 16.0, 520.0, 50.0, -45.0, 75.0, 60.0),
    "air": MoveFrameData("air", 5, 4, 10, 9.0, 300.0, 40.0, -35.0, 60.0, 50.0),
    "slam": MoveFrameData("slam", 8, 6, 14, 12.0, 350.0, 0.0, 10.0, 60.0, 50.0, is_downward_spike=True),
    "dash_attack": MoveFrameData("dash_attack", 6, 5, 12, 10.0, 380.0, 45.0, -45.0, 65.0, 50.0),
    "throw": MoveFrameData("throw", 8, 2, 14, 8.0, 400.0, 35.0, -45.0, 45.0, 50.0, is_unblockable=True),
}


class CombatState:
    def __init__(self, fighter_class: FighterClass):
        self.fighter_class = fighter_class
        stats = CLASS_STATS[fighter_class]

        self.max_health = stats.health
        self.health = stats.health
        self.max_guard = stats.max_guard
        self.guard = stats.max_guard
        self.power = 25.0  # Reset on KO to 25

        # Combat action states
        self.current_action: str = "idle"
        self.action_frame: int = 0
        self.has_hit_current_swing: bool = False
        self.charge_time: float = 0.0
        self.is_charging_heavy: bool = False

        # Dash timers
        self.dash_timer: float = 0.0
        self.dash_cooldown_timer: float = 0.0

        # Defense & Block
        self.is_blocking: bool = False
        self.block_held_time: float = 0.0

        # Stun & Hit-stop
        self.stun_timer: float = 0.0
        self.hit_stop_frames: int = 0

        # Rage Mode
        self.is_in_rage: bool = False
        self.rage_timer: float = 0.0

        # Combos
        self.combo_count: int = 0
        self.combo_reset_timer: float = 0.0

        # Ninja passive: extra air dash
        self.has_used_air_dash: bool = False

        # Weapon state
        self.held_weapon_type: Optional[WeaponType] = None
        self.weapon_durability: int = 0
        self.weapon_max_durability: int = 0

        # Throwable
        self.held_throwable: Optional[str] = None

        # Special ability cooldown
        self.special_cooldown_timer: float = 0.0
        self.special_active_timer: float = 0.0

        # Status Manager
        self.statuses = StatusManager()

    def update(self, dt: float) -> List[Tuple[StatusType, float]]:
        # Hit stop freezes animations and actions
        if self.hit_stop_frames > 0:
            self.hit_stop_frames -= 1
            return []

        # Update stun
        if self.stun_timer > 0.0:
            self.stun_timer = max(0.0, self.stun_timer - dt)
            if self.stun_timer == 0.0:
                self.current_action = "idle"

        # Update dash
        if self.dash_timer > 0.0:
            self.dash_timer = max(0.0, self.dash_timer - dt)
        if self.dash_cooldown_timer > 0.0:
            self.dash_cooldown_timer = max(0.0, self.dash_cooldown_timer - dt)

        # Update special cooldown
        if self.special_cooldown_timer > 0.0:
            self.special_cooldown_timer = max(0.0, self.special_cooldown_timer - dt)
        if self.special_active_timer > 0.0:
            self.special_active_timer = max(0.0, self.special_active_timer - dt)

        # Update Rage mode
        if self.is_in_rage:
            self.rage_timer -= dt
            # Regenerate 2 health/sec during rage
            self.health = min(self.max_health, self.health + RAGE_HEALTH_REGEN * dt)
            if self.rage_timer <= 0.0:
                self.is_in_rage = False
                self.rage_timer = 0.0

        # Guard regeneration when not blocking
        if not self.is_blocking and self.guard < self.max_guard and self.stun_timer <= 0.0:
            self.guard = min(self.max_guard, self.guard + 15.0 * dt)

        if self.is_blocking:
            self.block_held_time += dt

        # Combo timer
        if self.combo_reset_timer > 0.0:
            self.combo_reset_timer -= dt
            if self.combo_reset_timer <= 0.0:
                self.combo_count = 0

        # Advance action frame
        if self.current_action in MOVE_TABLE:
            move = MOVE_TABLE[self.current_action]
            total_frames = move.startup_frames + move.active_frames + move.recovery_frames
            self.action_frame += 1
            if self.action_frame >= total_frames:
                self.current_action = "idle"
                self.action_frame = 0
                self.has_hit_current_swing = False

        # Status effect ticks
        tick_damages = self.statuses.update(dt)
        return tick_damages

    def get_attack_hitbox(self, player_x: float, player_y: float, facing: int) -> Optional[AABB]:
        if self.current_action not in MOVE_TABLE:
            return None

        move = MOVE_TABLE[self.current_action]
        # Active window check
        start = move.startup_frames
        end = move.startup_frames + move.active_frames
        if not (start <= self.action_frame < end):
            return None

        hx = player_x + (move.hitbox_offset_x * facing)
        hy = player_y + move.hitbox_offset_y
        return AABB(hx, hy, move.hitbox_w, move.hitbox_h)

    def can_act(self) -> bool:
        if self.stun_timer > 0.0 or self.hit_stop_frames > 0:
            return False
        if self.statuses.has_status(StatusType.FREEZE) or self.statuses.has_status(StatusType.STUN):
            return False
        return True

    def start_attack(self, move_name: str) -> bool:
        if not self.can_act():
            return False
        if self.current_action != "idle" and self.current_action not in ["light1", "light2"]:
            return False

        # Light combo chaining
        if move_name == "light":
            if self.current_action == "idle":
                self.current_action = "light1"
            elif self.current_action == "light1" and self.action_frame >= 6:
                self.current_action = "light2"
            elif self.current_action == "light2" and self.action_frame >= 6:
                self.current_action = "light3"
            else:
                return False
        else:
            self.current_action = move_name

        self.action_frame = 0
        self.has_hit_current_swing = False
        return True

    def start_dash(self, is_grounded: bool) -> bool:
        if not self.can_act():
            return False
        if self.dash_cooldown_timer > 0.0:
            return False

        # Ninja extra air dash passive
        if not is_grounded:
            if self.fighter_class == FighterClass.NINJA:
                if self.has_used_air_dash:
                    return False
                self.has_used_air_dash = True
            else:
                return False

        # Dash cancels any attack recovery
        self.current_action = "dash"
        self.action_frame = 0
        self.dash_timer = 0.16
        self.dash_cooldown_timer = 1.0
        return True

    def start_block(self) -> None:
        if self.can_act() and not self.is_blocking:
            self.is_blocking = True
            self.block_held_time = 0.0

    def stop_block(self) -> None:
        self.is_blocking = False
        self.block_held_time = 0.0

    def trigger_rage(self) -> bool:
        if self.power >= RAGE_POWER_COST and not self.is_in_rage:
            self.power = 0.0
            self.is_in_rage = True
            self.rage_timer = RAGE_DURATION
            return True
        return False

    def trigger_special(self) -> bool:
        cost = SPECIAL_POWER_COST_RAGE if self.is_in_rage else SPECIAL_POWER_COST
        if self.power >= cost and self.special_cooldown_timer <= 0.0 and self.can_act():
            self.power -= cost
            stats = CLASS_STATS[self.fighter_class]
            self.special_cooldown_timer = stats.special_cooldown
            self.special_active_timer = 0.4
            self.current_action = "special"
            self.action_frame = 0
            return True
        return False


def calculate_hit(
    attacker_state: CombatState,
    target_state: CombatState,
    move_name: str,
    target_body: PhysicsBody,
    attacker_facing: int,
    charge_multiplier: float = 1.0,
) -> Dict[str, Any]:
    """Calculates full damage, parry check, knockback velocity, hit-stun, and hit-stop."""
    move = MOVE_TABLE.get(move_name, MOVE_TABLE["light1"])
    attacker_stats = CLASS_STATS[attacker_state.fighter_class]
    target_stats = CLASS_STATS[target_state.fighter_class]

    # 1. Check Parry window (block pressed within first 8 frames = 0.133s)
    if (
        target_state.is_blocking
        and target_state.block_held_time <= PARRY_WINDOW_SECS
        and not move.is_unblockable
    ):
        # Parry successful!
        attacker_state.stun_timer = PARRY_STUN_DURATION
        target_state.power = min(MAX_POWER, target_state.power + PARRY_POWER_GAIN)
        return {
            "type": "parry",
            "damage": 0.0,
            "knockback_vx": 0.0,
            "knockback_vy": 0.0,
            "hit_stun": 0.0,
            "hit_stop": 6,
            "target_ko": False,
        }

    # 2. Base damage & multipliers
    base_dmg = move.damage * charge_multiplier
    if attacker_state.held_weapon_type:
        from .weapons import WEAPON_DEFINITIONS
        w_def = WEAPON_DEFINITIONS[attacker_state.held_weapon_type]
        base_dmg = w_def.damage

    # Rage mode +30% damage
    rage_mult = (1.0 + RAGE_DAMAGE_BUFF) if attacker_state.is_in_rage else 1.0
    status_mult = 1.2 if target_state.statuses.has_status(StatusType.FREEZE) else 1.0  # +20% dmg when frozen

    # Combo scaling: beyond 3rd hit, -10% per hit, min 50%
    combo_mult = max(0.5, 1.0 - max(0, attacker_state.combo_count - 3) * 0.10)

    final_dmg = base_dmg * attacker_stats.damage_mult * rage_mult * status_mult * combo_mult

    # 3. Blocking reduction & Guard meter drain
    was_blocking = target_state.is_blocking and not move.is_unblockable
    knockback_reduction = 1.0
    if was_blocking:
        final_dmg *= (1.0 - BLOCK_DAMAGE_REDUCTION)
        knockback_reduction = (1.0 - BLOCK_KNOCKBACK_REDUCTION)
        target_state.guard -= final_dmg
        if target_state.guard <= 0.0:
            # Guard break stun!
            target_state.guard = 0.0
            target_state.is_blocking = False
            target_state.stun_timer = GUARD_BREAK_STUN

    # 4. Shield status absorption
    remaining_dmg, shield_broke = target_state.statuses.absorb_damage(final_dmg)

    # 5. Apply health damage
    target_state.health = max(0.0, target_state.health - remaining_dmg)
    target_ko = target_state.health <= 0.0

    # 6. Power meter gains
    attacker_state.power = min(MAX_POWER, attacker_state.power + remaining_dmg * 0.6)
    target_state.power = min(MAX_POWER, target_state.power + remaining_dmg * 0.4)

    # 7. Knockback calculation (Section 5.4)
    # Launch speed = base_knockback * (1 + 1.5 * (1 - current_hp / max_hp)) / target_weight
    hp_ratio = target_state.health / target_state.max_health
    launch_speed = (
        move.base_knockback
        * (1.0 + 1.5 * (1.0 - hp_ratio))
        / target_stats.weight
        * knockback_reduction
    )

    if move.is_downward_spike:
        kb_vx = (launch_speed * 0.3) * attacker_facing
        kb_vy = launch_speed * 0.95  # Slam down
    else:
        kb_vx = (launch_speed * 0.8) * attacker_facing
        kb_vy = -launch_speed * 0.6   # Knock upward

    target_body.vx = kb_vx
    target_body.vy = kb_vy
    target_body.is_grounded = False

    # 8. Hit-stun: 0.10s + launch_speed / 4000, capped at 0.5s
    hit_stun = min(0.5, 0.10 + launch_speed / 4000.0)
    target_state.stun_timer = max(target_state.stun_timer, hit_stun)

    # 9. Hit-stop: 3f light, 6f heavy, 10f KO
    if target_ko:
        hit_stop = 10
    elif move_name == "heavy" or move_name == "slam":
        hit_stop = 6
    else:
        hit_stop = 3
    attacker_state.hit_stop_frames = hit_stop
    target_state.hit_stop_frames = hit_stop

    # 10. Update combo counter
    attacker_state.combo_count += 1
    attacker_state.combo_reset_timer = 1.5

    # Weapon durability loss
    if attacker_state.held_weapon_type:
        attacker_state.weapon_durability -= 1
        if attacker_state.weapon_durability <= 0:
            attacker_state.held_weapon_type = None

    return {
        "type": "hit",
        "damage": round(final_dmg, 1),
        "knockback_vx": round(kb_vx, 1),
        "knockback_vy": round(kb_vy, 1),
        "hit_stun": round(hit_stun, 2),
        "hit_stop": hit_stop,
        "target_ko": target_ko,
        "shield_broke": shield_broke,
    }
