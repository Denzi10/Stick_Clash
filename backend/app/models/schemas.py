"""Pydantic schemas and dataclasses for Stick Clash game networking and state."""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class FighterClass(str, Enum):
    BRAWLER = "brawler"
    NINJA = "ninja"
    MAGE = "mage"
    BRUISER = "bruiser"


class GameMode(str, Enum):
    DUEL = "duel"
    TEAM_CLASH = "team_clash"
    FFA = "ffa"
    GAUNTLET = "gauntlet"


class StatusType(str, Enum):
    BURN = "burn"
    FREEZE = "freeze"
    SHOCK = "shock"
    POISON = "poison"
    SLOW = "slow"
    STUN = "stun"
    SHIELD = "shield"
    RAGE = "rage"


class WeaponType(str, Enum):
    SWORD = "sword"
    BAT = "bat"
    HAMMER = "hammer"
    NUNCHUCKS = "nunchucks"
    SPEAR = "spear"
    BOW = "bow"
    PISTOL = "pistol"
    BOOMERANG = "boomerang"


class ItemType(str, Enum):
    BOMB = "bomb"
    BANANA = "banana"
    SNOWBALL = "snowball"
    FROST_ORB = "frost_orb"
    STICKY_TRAP = "sticky_trap"
    HEALTH_PACK = "health_pack"
    ENERGY_DRINK = "energy_drink"
    SPEED_BOOST = "speed_boost"
    DOUBLE_DAMAGE = "double_damage"
    SHIELD_BUBBLE = "shield_bubble"
    GIANT = "giant"
    GHOST = "ghost"


class InputBitmask:
    LEFT = 1 << 0
    RIGHT = 1 << 1
    UP = 1 << 2        # Jump
    DOWN = 1 << 3      # Drop through / crouch / fast-fall
    LIGHT = 1 << 4     # Light attack
    HEAVY = 1 << 5     # Heavy attack (hold to charge)
    SPECIAL = 1 << 6   # Special ability
    DASH = 1 << 7      # Dash
    BLOCK = 1 << 8     # Block / Parry
    GRAB = 1 << 9      # Grab / Pickup / Throw
    RAGE = 1 << 10     # Activate Rage mode
    EMOTE = 1 << 11    # Emote wheel trigger


class StatusState(BaseModel):
    status_type: StatusType
    remaining_secs: float
    total_secs: float
    tick_timer: float = 0.0


class HeldWeaponState(BaseModel):
    weapon_type: WeaponType
    durability: int
    max_durability: int


class PlayerSnapshot(BaseModel):
    id: str
    nickname: str
    fighter_class: FighterClass
    team: int
    x: float
    y: float
    vx: float
    vy: float
    facing: int  # 1 for right, -1 for left
    is_grounded: bool
    is_crouching: bool
    is_dashing: bool
    is_blocking: bool
    is_ragdoll: bool
    is_invulnerable: bool
    action_state: str  # idle, run, jump, fall, light1, light2, light3, heavy, charge, air, slam, dash, stun, etc.
    action_frame: int
    health: float
    max_health: float
    power: float
    guard: float
    max_guard: float
    statuses: List[StatusState] = []
    held_weapon: Optional[HeldWeaponState] = None
    held_throwable: Optional[ItemType] = None
    score: int = 0
    kills: int = 0
    deaths: int = 0
    assists: int = 0
    combo_count: int = 0
    is_bot: bool = False
    connected: bool = True


class ProjectileSnapshot(BaseModel):
    id: str
    owner_id: str
    item_type: Optional[str] = None
    x: float
    y: float
    vx: float
    vy: float
    radius: float
    damage: float
    time_left: float


class PickupSnapshot(BaseModel):
    id: str
    item_type: str
    is_weapon: bool
    x: float
    y: float
    vx: float
    vy: float
    rarity: str
    despawn_timer: float


class HazardSnapshot(BaseModel):
    id: str
    hazard_type: str
    x: float
    y: float
    width: float
    height: float
    active: bool = True
    param: float = 0.0  # e.g. rising lava level or conveyor speed


class DiscreteEvent(BaseModel):
    event_type: str  # hit, ko, parry, guard_break, pickup, status_apply, special, rage, hazard_hit, level_complete
    data: Dict[str, Any]


class MatchSnapshot(BaseModel):
    tick: int
    match_time_remaining: float
    mode: GameMode
    arena_id: str
    players: List[PlayerSnapshot]
    projectiles: List[ProjectileSnapshot] = []
    pickups: List[PickupSnapshot] = []
    hazards: List[HazardSnapshot] = []
    events: List[DiscreteEvent] = []
    objective_info: Dict[str, Any] = {}
    is_game_over: bool = False
    winning_team: Optional[int] = None
    winner_id: Optional[str] = None


class LobbyPlayer(BaseModel):
    id: str
    nickname: str
    fighter_class: FighterClass
    team: int
    is_host: bool
    is_ready: bool
    is_bot: bool = False
    bot_difficulty: str = "normal"  # easy, normal, hard


class RoomInfo(BaseModel):
    room_code: str
    mode: GameMode
    arena_id: str
    players_count: int
    max_players: int
    in_game: bool
    host_nickname: str
    target_score: int
    time_limit_secs: int
    gauntlet_variant: Optional[str] = None


class UpgradeOffer(BaseModel):
    id: str
    name: str
    description: str
    stat_key: str
    value: float
    current_stacks: int
    max_stacks: int
