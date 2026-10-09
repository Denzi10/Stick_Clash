"""Items, Pickups, Crates, and Projectile simulation."""

import math
import random
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from ..config import CANVAS_WIDTH, CANVAS_HEIGHT, TICK_DT
from ..models.schemas import ItemType, WeaponType, PickupSnapshot, ProjectileSnapshot, StatusType
from .weapons import WEAPON_DEFINITIONS


@dataclass
class PickupEntity:
    id: str
    item_type: str  # Either WeaponType or ItemType string
    is_weapon: bool
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    rarity: str = "common"
    despawn_timer: float = 20.0  # Despawns after 20s, blinks last 4s
    on_ground: bool = False

    def update(self, dt: float, platforms: list) -> None:
        self.despawn_timer -= dt

        if not self.on_ground:
            self.vy += 800.0 * dt
            self.y += self.vy * dt
            self.x += self.vx * dt

            # Ground collision check
            for p in platforms:
                pa = p.to_aabb()
                if (pa.left <= self.x <= pa.right) and (self.y >= pa.top) and (self.y - self.vy * dt <= pa.top + 10):
                    self.y = pa.top - 8.0
                    self.vy = 0.0
                    self.vx = 0.0
                    self.on_ground = True
                    break

            if self.y > CANVAS_HEIGHT - 30:
                self.y = CANVAS_HEIGHT - 30
                self.vy = 0.0
                self.vx = 0.0
                self.on_ground = True


@dataclass
class ProjectileEntity:
    id: str
    owner_id: str
    projectile_type: str  # arrow, bullet, boomerang, arcane_bolt, elemental_blast, bomb, snowball, frost_orb
    x: float
    y: float
    vx: float
    vy: float
    radius: float
    damage: float
    time_left: float
    applies_status: Optional[StatusType] = None
    is_returning: bool = False
    return_speed: float = 550.0

    def update(self, dt: float, owner_x: float, owner_y: float) -> bool:
        """Returns True if still alive, False if expired."""
        self.time_left -= dt
        if self.time_left <= 0.0:
            return False

        if self.projectile_type == "boomerang":
            # If past half lifetime, fly back toward owner
            if self.time_left < 0.75:
                dx = owner_x - self.x
                dy = (owner_y - 45.0) - self.y
                dist = math.hypot(dx, dy)
                if dist < 30.0:
                    return False  # Caught by owner
                if dist > 0.1:
                    self.vx = (dx / dist) * self.return_speed
                    self.vy = (dy / dist) * self.return_speed
            self.x += self.vx * dt
            self.y += self.vy * dt
            return True

        if self.projectile_type == "bomb":
            # Gravity on thrown bomb
            self.vy += 800.0 * dt

        self.x += self.vx * dt
        self.y += self.vy * dt

        # Boundary checks
        if self.x < -50 or self.x > CANVAS_WIDTH + 50 or self.y < -50 or self.y > CANVAS_HEIGHT + 50:
            return False

        return True


class ItemSystem:
    def __init__(self):
        self.pickups: Dict[str, PickupEntity] = {}
        self.projectiles: Dict[str, ProjectileEntity] = {}
        self.crate_timer = 9.0  # Crate drops every 8 to 12s
        self.max_pickups = 3

    def update(self, dt: float, platforms: list, player_positions: Dict[str, Tuple[float, float]]) -> None:
        # Crate drop timer
        self.crate_timer -= dt
        if self.crate_timer <= 0.0:
            self.crate_timer = random.uniform(8.0, 12.0)
            if len(self.pickups) < self.max_pickups:
                self.spawn_random_crate()

        # Update pickups
        for p_id in list(self.pickups.keys()):
            p = self.pickups[p_id]
            p.update(dt, platforms)
            if p.despawn_timer <= 0.0:
                del self.pickups[p_id]

        # Update projectiles
        for p_id in list(self.projectiles.keys()):
            proj = self.projectiles[p_id]
            owner_pos = player_positions.get(proj.owner_id, (proj.x, proj.y))
            alive = proj.update(dt, owner_pos[0], owner_pos[1])
            if not alive:
                del self.projectiles[p_id]

    def spawn_random_crate(self) -> None:
        # Rarity: common 60%, rare 30%, epic 10%
        roll = random.random()
        drop_x = random.uniform(150, CANVAS_WIDTH - 150)
        drop_y = 20.0

        if roll < 0.60:
            # Common: Sword, Bat, Nunchucks, Health Pack, Energy Drink, Banana, Snowball
            rarity = "common"
            choices = [
                (WeaponType.SWORD.value, True),
                (WeaponType.BAT.value, True),
                (WeaponType.NUNCHUCKS.value, True),
                (ItemType.HEALTH_PACK.value, False),
                (ItemType.ENERGY_DRINK.value, False),
                (ItemType.BANANA.value, False),
                (ItemType.SNOWBALL.value, False),
            ]
        elif roll < 0.90:
            # Rare: Spear, Bow, Pistol, Boomerang, Bomb, Frost Orb, Sticky Trap, Speed Boost
            rarity = "rare"
            choices = [
                (WeaponType.SPEAR.value, True),
                (WeaponType.BOW.value, True),
                (WeaponType.PISTOL.value, True),
                (WeaponType.BOOMERANG.value, True),
                (ItemType.BOMB.value, False),
                (ItemType.FROST_ORB.value, False),
                (ItemType.STICKY_TRAP.value, False),
                (ItemType.SPEED_BOOST.value, False),
            ]
        else:
            # Epic: Hammer, Double Damage, Shield Bubble, Giant, Ghost
            rarity = "epic"
            choices = [
                (WeaponType.HAMMER.value, True),
                (ItemType.DOUBLE_DAMAGE.value, False),
                (ItemType.SHIELD_BUBBLE.value, False),
                (ItemType.GIANT.value, False),
                (ItemType.GHOST.value, False),
            ]

        item_choice, is_w = random.choice(choices)
        pickup = PickupEntity(
            id=str(uuid.uuid4())[:8],
            item_type=item_choice,
            is_weapon=is_w,
            x=drop_x,
            y=drop_y,
            vy=120.0,
            rarity=rarity,
        )
        self.pickups[pickup.id] = pickup

    def spawn_fixed_pickup(self, item_type: str, is_weapon: bool, x: float, y: float, rarity: str = "common") -> None:
        p = PickupEntity(
            id=str(uuid.uuid4())[:8],
            item_type=item_type,
            is_weapon=is_weapon,
            x=x,
            y=y,
            rarity=rarity,
            on_ground=True,
        )
        self.pickups[p.id] = p

    def add_projectile(
        self,
        owner_id: str,
        proj_type: str,
        x: float,
        y: float,
        vx: float,
        vy: float,
        damage: float,
        lifetime: float = 2.0,
        radius: float = 8.0,
        status: Optional[StatusType] = None,
    ) -> ProjectileEntity:
        p = ProjectileEntity(
            id=str(uuid.uuid4())[:8],
            owner_id=owner_id,
            projectile_type=proj_type,
            x=x,
            y=y,
            vx=vx,
            vy=vy,
            radius=radius,
            damage=damage,
            time_left=lifetime,
            applies_status=status,
        )
        self.projectiles[p.id] = p
        return p

    def to_snapshots(self) -> Tuple[List[PickupSnapshot], List[ProjectileSnapshot]]:
        pickups_list = [
            PickupSnapshot(
                id=p.id,
                item_type=p.item_type,
                is_weapon=p.is_weapon,
                x=round(p.x, 1),
                y=round(p.y, 1),
                vx=round(p.vx, 1),
                vy=round(p.vy, 1),
                rarity=p.rarity,
                despawn_timer=round(p.despawn_timer, 1),
            )
            for p in self.pickups.values()
        ]
        projs_list = [
            ProjectileSnapshot(
                id=pr.id,
                owner_id=pr.owner_id,
                item_type=pr.projectile_type,
                x=round(pr.x, 1),
                y=round(pr.y, 1),
                vx=round(pr.vx, 1),
                vy=round(pr.vy, 1),
                radius=pr.radius,
                damage=pr.damage,
                time_left=round(pr.time_left, 2),
            )
            for pr in self.projectiles.values()
        ]
        return pickups_list, projs_list
