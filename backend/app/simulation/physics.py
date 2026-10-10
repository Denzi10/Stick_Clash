"""Deterministic 2D AABB Physics Engine for Stick Clash."""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from ..config import (
    CANVAS_WIDTH,
    CANVAS_HEIGHT,
    TICK_DT,
    GRAVITY,
    GROUND_ACCEL,
    AIR_CONTROL,
    JUMP_VELOCITY,
    DOUBLE_JUMP_VELOCITY,
    MAX_FALL_SPEED,
    FAST_FALL_SPEED,
    HURTBOX_WIDTH,
    HURTBOX_HEIGHT,
    HURTBOX_CROUCH_HEIGHT,
)


@dataclass
class AABB:
    x: float
    y: float
    width: float
    height: float

    @property
    def left(self) -> float:
        return self.x - self.width / 2.0

    @property
    def right(self) -> float:
        return self.x + self.width / 2.0

    @property
    def top(self) -> float:
        return self.y - self.height / 2.0

    @property
    def bottom(self) -> float:
        return self.y + self.height / 2.0

    def overlaps(self, other: "AABB") -> bool:
        return not (
            self.right <= other.left
            or self.left >= other.right
            or self.bottom <= other.top
            or self.top >= other.bottom
        )

    def contains_point(self, px: float, py: float) -> bool:
        return self.left <= px <= self.right and self.top <= py <= self.bottom


@dataclass
class Platform:
    id: str
    x: float
    y: float
    width: float
    height: float
    is_solid: bool = False   # True = blocks all directions, False = one-way (can jump up through)
    is_moving: bool = False
    vx: float = 0.0
    vy: float = 0.0
    path_min_x: float = 0.0
    path_max_x: float = 0.0
    is_slippery: bool = False  # e.g. Snow Peaks
    friction: float = 1.0
    is_crumbly: bool = False   # Sky Islands
    crumble_timer: float = 0.0
    is_broken: bool = False

    def to_aabb(self) -> AABB:
        return AABB(self.x, self.y, self.width, self.height)

    def update(self, dt: float) -> None:
        if self.is_moving:
            self.x += self.vx * dt
            if self.x > self.path_max_x:
                self.x = self.path_max_x
                self.vx = -abs(self.vx)
            elif self.x < self.path_min_x:
                self.x = self.path_min_x
                self.vx = abs(self.vx)

        if self.is_crumbly and self.crumble_timer > 0.0:
            self.crumble_timer -= dt
            if self.crumble_timer <= 0.0:
                self.is_broken = True


@dataclass
class PhysicsBody:
    x: float = 0.0
    y: float = 0.0
    vx: float = 0.0
    vy: float = 0.0
    width: float = HURTBOX_WIDTH
    height: float = HURTBOX_HEIGHT
    is_grounded: bool = False
    is_crouching: bool = False
    can_double_jump: bool = True
    jump_count: int = 0
    max_jumps: int = 3  # Triple jump for high mobility!
    jump_debounce: float = 0.0  # Prevents instant double jump on held key
    drop_through_timer: float = 0.0
    wrap_horizontal: bool = True
    on_conveyor_vx: float = 0.0
    external_force_x: float = 0.0
    external_force_y: float = 0.0

    def get_aabb(self) -> AABB:
        h = HURTBOX_CROUCH_HEIGHT if self.is_crouching else HURTBOX_HEIGHT
        return AABB(self.x, self.y - (h / 2.0), self.width, h)

    def step(
        self,
        dt: float,
        target_vx: float,
        accel_scale: float,
        fast_fall: bool,
        platforms: List[Platform],
        friction: float = 1.0,
    ) -> None:
        # 1. Horizontal acceleration
        accel = GROUND_ACCEL * accel_scale if self.is_grounded else GROUND_ACCEL * accel_scale * AIR_CONTROL
        accel *= friction

        if target_vx > self.vx:
            self.vx = min(target_vx, self.vx + accel * dt)
        elif target_vx < self.vx:
            self.vx = max(target_vx, self.vx - accel * dt)
        else:
            # Friction / Deceleration towards 0
            if self.vx > 0:
                self.vx = max(0.0, self.vx - accel * dt)
            elif self.vx < 0:
                self.vx = min(0.0, self.vx + accel * dt)

        # Apply external forces (wind gusts, conveyor belts)
        self.vx += (self.on_conveyor_vx + self.external_force_x) * dt
        self.vy += self.external_force_y * dt

        # 2. Gravity & vertical velocity
        prev_y = self.y
        prev_bottom = prev_y

        self.vy += GRAVITY * dt
        max_fall = FAST_FALL_SPEED if fast_fall else MAX_FALL_SPEED
        if self.vy > max_fall:
            self.vy = max_fall

        # 3. Position update
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Drop-through timer update
        if self.drop_through_timer > 0.0:
            self.drop_through_timer = max(0.0, self.drop_through_timer - dt)

        # Jump debounce countdown
        if self.jump_debounce > 0.0:
            self.jump_debounce = max(0.0, self.jump_debounce - dt)

        # 4. Horizontal wrap-around or boundary clamp
        if self.wrap_horizontal:
            if self.x < 0:
                self.x += CANVAS_WIDTH
            elif self.x > CANVAS_WIDTH:
                self.x -= CANVAS_WIDTH
        else:
            half_w = self.width / 2.0
            if self.x - half_w < 0:
                self.x = half_w
                self.vx = 0.0
            elif self.x + half_w > CANVAS_WIDTH:
                self.x = CANVAS_WIDTH - half_w
                self.vx = 0.0

        # 5. Collision resolution against platforms
        self.is_grounded = False
        curr_bottom = self.y
        half_w = self.width / 2.0

        for p in platforms:
            if p.is_broken:
                continue

            pa = p.to_aabb()

            if p.is_solid:
                # Solid box collision: top, bottom, sides
                ba = self.get_aabb()
                if ba.overlaps(pa):
                    # Resolve along least penetration axis
                    overlap_x1 = ba.right - pa.left
                    overlap_x2 = pa.right - ba.left
                    overlap_y1 = ba.bottom - pa.top
                    overlap_y2 = pa.bottom - ba.top

                    min_overlap = min(overlap_x1, overlap_x2, overlap_y1, overlap_y2)

                    if min_overlap == overlap_y1 and self.vy >= 0:
                        # Landed on top of solid platform
                        self.y = pa.top
                        self.vy = 0.0
                        self.is_grounded = True
                        self.jump_count = 0
                        if p.is_crumbly and p.crumble_timer == 0.0:
                            p.crumble_timer = 2.0
                    elif min_overlap == overlap_y2 and self.vy < 0:
                        # Hit ceiling
                        self.y = pa.bottom + (ba.height)
                        self.vy = 0.0
                    elif min_overlap == overlap_x1:
                        self.x = pa.left - half_w
                        self.vx = 0.0
                    elif min_overlap == overlap_x2:
                        self.x = pa.right + half_w
                        self.vx = 0.0
            else:
                # One-way / Thin platform:
                # Only check if falling downward and player feet crossed platform surface
                if self.vy >= 0.0 and self.drop_through_timer <= 0.0:
                    # Feet horizontal check
                    if (self.x + half_w * 0.8 >= pa.left) and (self.x - half_w * 0.8 <= pa.right):
                        # Feet crossed from at or above platform top to below platform top
                        plat_top = pa.top
                        if prev_bottom <= plat_top + 12.0 and curr_bottom >= plat_top:
                            self.y = plat_top
                            self.vy = 0.0
                            self.is_grounded = True
                            self.jump_count = 0
                            if p.is_crumbly and p.crumble_timer == 0.0:
                                p.crumble_timer = 2.0

        # Bottom abyss boundary
        if self.y > CANVAS_HEIGHT + 40.0:
            self.y = CANVAS_HEIGHT + 40.0
            self.vy = 0.0

    def jump(self) -> bool:
        if self.jump_debounce > 0.0:
            return False
        if self.is_grounded or self.jump_count == 0:
            self.vy = JUMP_VELOCITY
            self.is_grounded = False
            self.jump_count = 1
            self.jump_debounce = 0.12
            return True
        elif self.jump_count < self.max_jumps:
            self.vy = DOUBLE_JUMP_VELOCITY
            self.jump_count += 1
            self.jump_debounce = 0.12
            return True
        return False

    def drop_through(self) -> None:
        self.drop_through_timer = 0.35  # Ignore one-way collisions for 0.35s
        self.is_grounded = False
