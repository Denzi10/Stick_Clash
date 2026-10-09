"""Room and Match Simulation Coordinator for Stick Clash.
Runs authoritative 60 Hz simulation and broadcasts 20 Hz snapshots.
"""

import asyncio
import math
import random
import time
import uuid
from typing import Dict, List, Optional, Tuple, Any, Set
from fastapi import WebSocket

from ..config import (
    SIMULATION_HZ,
    TICK_DT,
    SNAPSHOT_INTERVAL_TICKS,
    DISCONNECT_HOLD_SECS,
    RESPAWN_DELAY_SECS,
    RESPAWN_INVULN_SECS,
    DASH_SPEED,
    DASH_INVULN_DURATION,
)
from ..models.schemas import (
    GameMode,
    FighterClass,
    InputBitmask,
    PlayerSnapshot,
    HeldWeaponState,
    MatchSnapshot,
    DiscreteEvent,
    LobbyPlayer,
    StatusType,
)
from ..simulation.physics import PhysicsBody, Platform
from ..simulation.combat import CombatState, calculate_hit, MOVE_TABLE
from ..simulation.classes import CLASS_STATS
from ..simulation.arenas import ArenaManager
from ..simulation.items import ItemSystem
from ..simulation.weapons import WEAPON_DEFINITIONS
from ..modes import DuelMode, TeamClashMode, FreeForAllMode, GauntletMode
from ..bot.ai import BotAI


class PlayerEntity:
    def __init__(
        self,
        player_id: str,
        nickname: str,
        fighter_class: FighterClass,
        team: int = 0,
        is_bot: bool = False,
        bot_difficulty: str = "normal",
    ):
        self.id = player_id
        self.nickname = nickname
        self.fighter_class = fighter_class
        self.team = team
        self.is_bot = is_bot
        self.bot_difficulty = bot_difficulty
        self.bot_ai = BotAI(player_id, bot_difficulty) if is_bot else None

        self.physics = PhysicsBody()
        self.combat = CombatState(fighter_class)
        self.facing = 1  # 1 right, -1 left
        self.is_invulnerable = False
        self.invuln_timer = 0.0
        self.respawn_timer = 0.0

        # Disconnection handling
        self.connected = True
        self.disconnected_at: Optional[float] = None

        # Network input buffer
        self.latest_input_bitmask = 0
        self.input_sequence = 0

    def apply_inputs(self, bitmask: int, dt: float, platforms: List[Platform], arena_wrap: bool) -> None:
        self.physics.wrap_horizontal = arena_wrap
        stats = CLASS_STATS[self.fighter_class]

        # Rage activation
        if bitmask & InputBitmask.RAGE:
            self.combat.trigger_rage()

        # Special ability
        if bitmask & InputBitmask.SPECIAL:
            self.combat.trigger_special()

        # Block & Parry
        if bitmask & InputBitmask.BLOCK:
            self.combat.start_block()
        else:
            self.combat.stop_block()

        # Dash
        if bitmask & InputBitmask.DASH:
            if self.combat.start_dash(self.physics.is_grounded):
                # Dash boost
                self.physics.vx = DASH_SPEED * self.facing

        # Attacks
        if self.combat.can_act():
            if bitmask & InputBitmask.LIGHT:
                if not self.physics.is_grounded:
                    self.combat.start_attack("air")
                elif bitmask & InputBitmask.DOWN:
                    self.combat.start_attack("slam")
                elif self.combat.current_action == "dash":
                    self.combat.start_attack("dash_attack")
                else:
                    self.combat.start_attack("light")
            elif bitmask & InputBitmask.HEAVY:
                self.combat.start_attack("heavy")
            elif bitmask & InputBitmask.GRAB:
                self.combat.start_attack("throw")

        # Movement speed calculation
        base_speed = stats.speed
        if self.combat.is_in_rage:
            base_speed *= 1.15
        if self.combat.statuses.has_status(StatusType.SLOW):
            base_speed *= 0.60
        if self.combat.is_blocking:
            base_speed *= 0.30

        target_vx = 0.0
        if self.combat.can_act() and self.combat.current_action != "dash":
            if bitmask & InputBitmask.RIGHT:
                target_vx = base_speed
                self.facing = 1
            elif bitmask & InputBitmask.LEFT:
                target_vx = -base_speed
                self.facing = -1

            # Jump
            if bitmask & InputBitmask.UP:
                self.physics.jump()

            # Fast-fall & drop-through
            if bitmask & InputBitmask.DOWN:
                if self.physics.is_grounded:
                    self.physics.drop_through()
                self.physics.is_crouching = self.physics.is_grounded
            else:
                self.physics.is_crouching = False
        else:
            self.physics.is_crouching = False

        fast_fall = bool(bitmask & InputBitmask.DOWN and not self.physics.is_grounded)

        # Physics step
        accel_scale = 1.0
        self.physics.step(dt, target_vx, accel_scale, fast_fall, platforms)

        # Invulnerability countdown
        if self.invuln_timer > 0.0:
            self.invuln_timer -= dt
            if self.invuln_timer <= 0.0:
                self.is_invulnerable = False

    def to_snapshot(self, score: int, kills: int, deaths: int, assists: int) -> PlayerSnapshot:
        held_w = None
        if self.combat.held_weapon_type:
            held_w = HeldWeaponState(
                weapon_type=self.combat.held_weapon_type,
                durability=self.combat.weapon_durability,
                max_durability=self.combat.weapon_max_durability,
            )

        return PlayerSnapshot(
            id=self.id,
            nickname=self.nickname,
            fighter_class=self.fighter_class,
            team=self.team,
            x=round(self.physics.x, 1),
            y=round(self.physics.y, 1),
            vx=round(self.physics.vx, 1),
            vy=round(self.physics.vy, 1),
            facing=self.facing,
            is_grounded=self.physics.is_grounded,
            is_crouching=self.physics.is_crouching,
            is_dashing=(self.combat.dash_timer > 0.0),
            is_blocking=self.combat.is_blocking,
            is_ragdoll=(self.combat.health <= 0.0),
            is_invulnerable=self.is_invulnerable or (self.combat.dash_timer > 0.16 - DASH_INVULN_DURATION),
            action_state=self.combat.current_action,
            action_frame=self.combat.action_frame,
            health=round(self.combat.health, 1),
            max_health=self.combat.max_health,
            power=round(self.combat.power, 1),
            guard=round(self.combat.guard, 1),
            max_guard=self.combat.max_guard,
            statuses=self.combat.statuses.to_snapshots(),
            held_weapon=held_w,
            held_throwable=self.combat.held_throwable,
            score=score,
            kills=kills,
            deaths=deaths,
            assists=assists,
            combo_count=self.combat.combo_count,
            is_bot=self.is_bot,
            connected=self.connected,
        )


class GameRoom:
    def __init__(
        self,
        room_code: str,
        mode: GameMode = GameMode.DUEL,
        arena_id: str = "training_dojo",
        max_players: int = 4,
    ):
        self.room_code = room_code
        self.mode_type = mode
        self.arena_id = arena_id
        self.max_players = max_players
        self.in_game = False
        self.tick = 0
        self.loop_task: Optional[asyncio.Task] = None

        # Sockets & Players
        self.connections: Dict[str, WebSocket] = {}
        self.players: Dict[str, PlayerEntity] = {}
        self.host_id: Optional[str] = None

        # Game Systems
        self.arena_manager = ArenaManager(arena_id)
        self.item_system = ItemSystem()
        self.game_mode = self.create_mode(mode)
        self.events_queue: List[DiscreteEvent] = []

    def create_mode(self, mode: GameMode):
        if mode == GameMode.DUEL:
            return DuelMode()
        elif mode == GameMode.TEAM_CLASH:
            return TeamClashMode()
        elif mode == GameMode.FFA:
            return FreeForAllMode()
        elif mode == GameMode.GAUNTLET:
            return GauntletMode()
        return FreeForAllMode()

    def add_player(
        self,
        player_id: str,
        nickname: str,
        fighter_class: FighterClass,
        team: int = 0,
        is_bot: bool = False,
        difficulty: str = "normal",
    ) -> PlayerEntity:
        entity = PlayerEntity(player_id, nickname, fighter_class, team, is_bot, difficulty)
        self.players[player_id] = entity
        if not self.host_id and not is_bot:
            self.host_id = player_id

        # Spawn placement
        self.respawn_player(entity)
        return entity

    def respawn_player(self, player: PlayerEntity) -> None:
        arena = self.arena_manager.current_arena
        # Pick spawn furthest from enemies
        best_spawn = arena.player_spawns[0]
        max_dist = -1.0

        for sp in arena.player_spawns:
            dist = 999999.0
            for other in self.players.values():
                if other.id != player.id and other.combat.health > 0.0:
                    d = math.hypot(sp[0] - other.physics.x, sp[1] - other.physics.y)
                    if d < dist:
                        dist = d
            if dist > max_dist:
                max_dist = dist
                best_spawn = sp

        player.physics.x = best_spawn[0]
        player.physics.y = best_spawn[1]
        player.physics.vx = 0.0
        player.physics.vy = 0.0
        player.combat.health = player.combat.max_health
        player.combat.guard = player.combat.max_guard
        player.combat.power = 25.0
        player.combat.current_action = "idle"
        player.combat.statuses.clear_all()
        player.is_invulnerable = True
        player.invuln_timer = RESPAWN_INVULN_SECS
        player.respawn_timer = 0.0

    async def start_game(self) -> None:
        self.in_game = True
        self.arena_manager.set_arena(self.arena_id)
        for p in self.players.values():
            self.respawn_player(p)
        self.loop_task = asyncio.create_task(self.game_loop())

    async def game_loop(self) -> None:
        tick_interval = TICK_DT
        next_tick_time = time.monotonic()

        while self.in_game:
            now = time.monotonic()
            if now < next_tick_time:
                await asyncio.sleep(max(0.001, next_tick_time - now))
            next_tick_time += tick_interval
            self.tick += 1

            self.step_simulation(TICK_DT)

            # Broadcast 20 Hz snapshot (every 3 ticks)
            if self.tick % SNAPSHOT_INTERVAL_TICKS == 0:
                await self.broadcast_snapshot()

    def step_simulation(self, dt: float) -> None:
        arena = self.arena_manager.current_arena
        self.arena_manager.update(dt)

        # 1. Update Disconnects & Bot AI
        now_time = time.time()
        for p in list(self.players.values()):
            if not p.connected and not p.is_bot and p.disconnected_at:
                if (now_time - p.disconnected_at) >= DISCONNECT_HOLD_SECS:
                    # Replace with bot
                    p.is_bot = True
                    p.bot_ai = BotAI(p.id, "normal")
                    self.events_queue.append(
                        DiscreteEvent(
                            event_type="bot_takeover",
                            data={"player_id": p.id, "nickname": p.nickname},
                        )
                    )

            if p.is_bot and p.bot_ai:
                others = [o for o in self.players.values() if o.id != p.id]
                p.latest_input_bitmask = p.bot_ai.decide_inputs(
                    dt, p, others, list(self.item_system.pickups.values())
                )

        # 2. Update players combat & physics
        for p in self.players.values():
            if p.combat.health <= 0.0:
                # Dead / Ragdoll
                p.respawn_timer += dt
                if p.respawn_timer >= RESPAWN_DELAY_SECS:
                    if self.mode_type != GameMode.DUEL:
                        self.respawn_player(p)
                continue

            # Update combat timers & status ticks
            tick_dots = p.combat.update(dt)
            for st_type, dot_dmg in tick_dots:
                p.combat.health = max(0.0, p.combat.health - dot_dmg)
                self.events_queue.append(
                    DiscreteEvent(
                        event_type="status_tick",
                        data={"player_id": p.id, "status": st_type.value, "damage": dot_dmg},
                    )
                )

            p.apply_inputs(p.latest_input_bitmask, dt, arena.platforms, arena.wrap_horizontal)

        # 3. Item System & Projectiles
        player_coords = {p.id: (p.physics.x, p.physics.y) for p in self.players.values()}
        self.item_system.update(dt, arena.platforms, player_coords)

        # 4. Resolve Combat Attacks & Hitboxes
        for attacker in self.players.values():
            if attacker.combat.health <= 0.0 or attacker.combat.has_hit_current_swing:
                continue

            atk_hitbox = attacker.combat.get_attack_hitbox(
                attacker.physics.x, attacker.physics.y, attacker.facing
            )
            if not atk_hitbox:
                continue

            for target in self.players.values():
                if target.id == attacker.id or target.combat.health <= 0.0 or target.is_invulnerable:
                    continue

                # Friendly fire rule: off in team clash
                if self.mode_type == GameMode.TEAM_CLASH and attacker.team == target.team:
                    continue

                target_box = target.physics.get_aabb()
                if atk_hitbox.overlaps(target_box):
                    # Landed a hit!
                    attacker.combat.has_hit_current_swing = True
                    result = calculate_hit(
                        attacker.combat,
                        target.combat,
                        attacker.combat.current_action,
                        target.physics,
                        attacker.facing,
                    )

                    if result["type"] == "parry":
                        self.events_queue.append(
                            DiscreteEvent(
                                event_type="parry",
                                data={"attacker_id": attacker.id, "defender_id": target.id},
                            )
                        )
                    else:
                        self.game_mode.register_damage(
                            attacker.id, target.id, result["damage"], now_time
                        )
                        self.events_queue.append(
                            DiscreteEvent(
                                event_type="hit",
                                data={
                                    "attacker_id": attacker.id,
                                    "target_id": target.id,
                                    "damage": result["damage"],
                                    "is_ko": result["target_ko"],
                                    "x": target.physics.x,
                                    "y": target.physics.y - 45.0,
                                },
                            )
                        )

                        if result["target_ko"]:
                            killer, assist = self.game_mode.process_kill(
                                target.id, attacker.id, now_time
                            )
                            self.events_queue.append(
                                DiscreteEvent(
                                    event_type="ko",
                                    data={"victim_id": target.id, "killer_id": killer, "assist_id": assist},
                                )
                            )

        # 5. Projectile Collisions
        for proj_id, proj in list(self.item_system.projectiles.items()):
            for target in self.players.values():
                if target.id == proj.owner_id or target.combat.health <= 0.0 or target.is_invulnerable:
                    continue
                tb = target.physics.get_aabb()
                if tb.contains_point(proj.x, proj.y):
                    # Projectile hit!
                    target.combat.health = max(0.0, target.combat.health - proj.damage)
                    is_ko = target.combat.health <= 0.0
                    target.physics.vx = proj.vx * 0.4
                    target.physics.vy = -180.0
                    target.physics.is_grounded = False

                    if proj.applies_status:
                        target.combat.statuses.apply_status(proj.applies_status, current_time=now_time)

                    self.game_mode.register_damage(proj.owner_id, target.id, proj.damage, now_time)
                    self.events_queue.append(
                        DiscreteEvent(
                            event_type="projectile_hit",
                            data={
                                "owner_id": proj.owner_id,
                                "target_id": target.id,
                                "damage": proj.damage,
                                "is_ko": is_ko,
                            },
                        )
                    )
                    if is_ko:
                        k, a = self.game_mode.process_kill(target.id, proj.owner_id, now_time)
                        self.events_queue.append(
                            DiscreteEvent(
                                event_type="ko",
                                data={"victim_id": target.id, "killer_id": k, "assist_id": a},
                            )
                        )

                    del self.item_system.projectiles[proj_id]
                    break

        # 6. Hazard Collisions
        for hazard in arena.hazards:
            if not hazard.active or hazard.damage <= 0.0 and hazard.push_y == 0.0:
                continue
            ha = AABB(hazard.x, hazard.y, hazard.width, hazard.height)
            for p in self.players.values():
                if p.combat.health <= 0.0 or p.is_invulnerable:
                    continue
                pa = p.physics.get_aabb()
                if ha.overlaps(pa):
                    if hazard.damage > 0.0:
                        p.combat.health = max(0.0, p.combat.health - hazard.damage * dt * 4.0)
                        if p.combat.health <= 0.0:
                            k, a = self.game_mode.process_kill(p.id, None, now_time)
                            self.events_queue.append(
                                DiscreteEvent(
                                    event_type="ko",
                                    data={"victim_id": p.id, "killer_id": None, "hazard": hazard.hazard_type},
                                )
                            )
                    if hazard.push_y != 0.0:
                        p.physics.vy = hazard.push_y
                        p.physics.is_grounded = False
                    if hazard.push_x != 0.0:
                        p.physics.vx += hazard.push_x * dt

        # 7. Update Game Mode
        self.game_mode.update(dt, list(self.players.values()))

    async def broadcast_snapshot(self) -> None:
        if not self.connections:
            return

        players_snap = [
            p.to_snapshot(
                score=self.game_mode.player_scores.get(p.id, 0),
                kills=self.game_mode.player_kills.get(p.id, 0),
                deaths=self.game_mode.player_deaths.get(p.id, 0),
                assists=self.game_mode.player_assists.get(p.id, 0),
            )
            for p in self.players.values()
        ]
        pickups_snap, projs_snap = self.item_system.to_snapshots()
        hazards_snap = self.arena_manager.get_hazard_snapshots()

        snapshot = MatchSnapshot(
            tick=self.tick,
            match_time_remaining=round(self.game_mode.time_remaining, 1),
            mode=self.mode_type,
            arena_id=self.arena_id,
            players=players_snap,
            projectiles=projs_snap,
            pickups=pickups_snap,
            hazards=hazards_snap,
            events=list(self.events_queue),
            objective_info=self.game_mode.get_objective_info(),
            is_game_over=self.game_mode.is_game_over,
            winning_team=self.game_mode.winning_team,
            winner_id=self.game_mode.winner_id,
        )
        self.events_queue.clear()

        payload = {"type": "snapshot", "data": snapshot.model_dump()}

        dead_connections = []
        for p_id, ws in self.connections.items():
            try:
                await ws.send_json(payload)
            except Exception:
                dead_connections.append(p_id)

        for p_id in dead_connections:
            del self.connections[p_id]
            if p_id in self.players:
                self.players[p_id].connected = False
                self.players[p_id].disconnected_at = time.time()
