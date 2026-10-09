"""Fighter class definitions, base stats, passives, and special moves."""

from dataclasses import dataclass
from typing import Dict
from ..models.schemas import FighterClass


@dataclass
class FighterClassStats:
    class_name: FighterClass
    health: float
    speed: float
    damage_mult: float
    weight: float
    max_guard: float
    special_name: str
    special_damage: float
    special_cooldown: float
    special_range: float
    description: str


CLASS_STATS: Dict[FighterClass, FighterClassStats] = {
    FighterClass.BRAWLER: FighterClassStats(
        class_name=FighterClass.BRAWLER,
        health=100.0,
        speed=300.0,
        damage_mult=1.0,
        weight=1.0,
        max_guard=50.0,  # Passive: +10 max guard (base 40 + 10)
        special_name="Quake Slam",
        special_damage=20.0,
        special_cooldown=6.0,
        special_range=180.0,  # 180 px radius, knockdown 0.8 s
        description="Balanced warrior with extended guard and heavy ground slams.",
    ),
    FighterClass.NINJA: FighterClassStats(
        class_name=FighterClass.NINJA,
        health=85.0,
        speed=345.0,
        damage_mult=0.9,
        weight=0.85,
        max_guard=40.0,
        special_name="Shadow Dash",
        special_damage=14.0,
        special_cooldown=6.0,
        special_range=320.0,  # 320 px dash through enemies
        description="Agile assassin with an extra mid-air dash and phasing strikes.",
    ),
    FighterClass.MAGE: FighterClassStats(
        class_name=FighterClass.MAGE,
        health=80.0,
        speed=285.0,
        damage_mult=0.95,
        weight=0.9,
        max_guard=40.0,
        special_name="Elemental Blast",
        special_damage=16.0,
        special_cooldown=5.0,
        special_range=600.0,  # projectile 16 damage, 600 px range
        description="Tactical caster with Arcane Bolt and alternating Freeze/Burn blasts.",
    ),
    FighterClass.BRUISER: FighterClassStats(
        class_name=FighterClass.BRUISER,
        health=130.0,
        speed=255.0,
        damage_mult=1.2,
        weight=1.3,
        max_guard=40.0,
        special_name="Charge Tackle",
        special_damage=18.0,
        special_cooldown=7.0,
        special_range=260.0,  # rush 260 px carrying enemies, stun 0.5s
        description="Heavy juggernaut with super armor during heavy attacks.",
    ),
}
