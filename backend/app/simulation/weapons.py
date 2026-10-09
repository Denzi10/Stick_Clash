"""Weapons system for Stick Clash."""

from dataclasses import dataclass
from typing import Dict, Optional
from ..models.schemas import WeaponType


@dataclass
class WeaponDef:
    weapon_type: WeaponType
    damage: float
    durability: int
    range_px: float
    is_ranged: bool
    projectile_speed: float = 0.0
    knockback_mult: float = 1.0
    rarity: str = "common"
    description: str = ""


WEAPON_DEFINITIONS: Dict[WeaponType, WeaponDef] = {
    WeaponType.SWORD: WeaponDef(
        weapon_type=WeaponType.SWORD,
        damage=12.0,
        durability=20,
        range_px=70.0,
        is_ranged=False,
        knockback_mult=1.0,
        rarity="common",
        description="Fast, balanced melee blade.",
    ),
    WeaponType.BAT: WeaponDef(
        weapon_type=WeaponType.BAT,
        damage=10.0,
        durability=18,
        range_px=65.0,
        is_ranged=False,
        knockback_mult=1.4,  # Spec: Knockback x1.4
        rarity="common",
        description="Heavy wooden bat that sends foes flying.",
    ),
    WeaponType.HAMMER: WeaponDef(
        weapon_type=WeaponType.HAMMER,
        damage=20.0,
        durability=10,
        range_px=80.0,
        is_ranged=False,
        knockback_mult=1.3,
        rarity="epic",  # Epic item
        description="Massive hammer that creates a ground shockwave.",
    ),
    WeaponType.NUNCHUCKS: WeaponDef(
        weapon_type=WeaponType.NUNCHUCKS,
        damage=6.0,
        durability=30,
        range_px=55.0,
        is_ranged=False,
        knockback_mult=0.8,
        rarity="common",
        description="Rapid multi-hit weapon with high durability.",
    ),
    WeaponType.SPEAR: WeaponDef(
        weapon_type=WeaponType.SPEAR,
        damage=11.0,
        durability=20,
        range_px=120.0,
        is_ranged=False,
        knockback_mult=1.1,
        rarity="rare",
        description="Extended reach polearm.",
    ),
    WeaponType.BOW: WeaponDef(
        weapon_type=WeaponType.BOW,
        damage=9.0,
        durability=8,
        range_px=500.0,
        is_ranged=True,
        projectile_speed=700.0,  # 700 px/s arrow
        rarity="rare",
        description="Ranged bow with charge for up to +50% damage.",
    ),
    WeaponType.PISTOL: WeaponDef(
        weapon_type=WeaponType.PISTOL,
        damage=6.0,
        durability=12,
        range_px=600.0,
        is_ranged=True,
        projectile_speed=900.0,  # 900 px/s bullet
        rarity="rare",
        description="Rapid fire sidearm (3 shots/sec).",
    ),
    WeaponType.BOOMERANG: WeaponDef(
        weapon_type=WeaponType.BOOMERANG,
        damage=8.0,
        durability=999,  # Unlimited durability
        range_px=400.0,
        is_ranged=True,
        projectile_speed=550.0,  # 400 px out and back
        rarity="rare",
        description="Returning projectile; only one in flight at a time.",
    ),
}
