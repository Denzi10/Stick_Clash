"""Unit tests for deterministic AABB physics and movement."""

import pytest
from app.simulation.physics import AABB, Platform, PhysicsBody
from app.config import (
    CANVAS_WIDTH,
    CANVAS_HEIGHT,
    JUMP_VELOCITY,
    DOUBLE_JUMP_VELOCITY,
    GRAVITY,
)


def test_aabb_overlaps():
    box1 = AABB(100, 100, 40, 90)
    box2 = AABB(110, 100, 40, 90)
    box3 = AABB(300, 300, 40, 90)

    assert box1.overlaps(box2) is True
    assert box1.overlaps(box3) is False


def test_jump_and_double_jump():
    body = PhysicsBody(x=100, y=500, is_grounded=True)
    assert body.jump() is True
    assert body.vy == JUMP_VELOCITY
    assert body.jump_count == 1
    assert body.is_grounded is False

    # Second jump in mid-air (double jump) after debounce
    body.jump_debounce = 0.0
    assert body.jump() is True
    assert body.vy == DOUBLE_JUMP_VELOCITY
    assert body.jump_count == 2

    # Third jump in mid-air (triple jump)
    body.jump_debounce = 0.0
    assert body.jump() is True
    assert body.vy == DOUBLE_JUMP_VELOCITY
    assert body.jump_count == 3

    # Fourth jump should fail (max 3 jumps)
    body.jump_debounce = 0.0
    assert body.jump() is False


def test_horizontal_wrap():
    body = PhysicsBody(x=-5, y=300, wrap_horizontal=True)
    body.step(dt=0.016, target_vx=0, accel_scale=1.0, fast_fall=False, platforms=[])
    assert body.x >= 0
    assert body.x <= CANVAS_WIDTH

    body.x = CANVAS_WIDTH + 10
    body.step(dt=0.016, target_vx=0, accel_scale=1.0, fast_fall=False, platforms=[])
    assert body.x <= CANVAS_WIDTH


def test_platform_landing():
    platform = Platform("floor", x=640, y=600, width=800, height=30, is_solid=True)
    body = PhysicsBody(x=640, y=580, vy=200, is_grounded=False)

    body.step(dt=0.1, target_vx=0, accel_scale=1.0, fast_fall=False, platforms=[platform])
    assert body.is_grounded is True
    assert body.vy == 0.0
    assert body.y <= platform.to_aabb().top + 1.0


def test_drop_through():
    platform = Platform("thin_plat", x=640, y=500, width=300, height=18, is_solid=False)
    body = PhysicsBody(x=640, y=500, is_grounded=True)

    body.drop_through()
    assert body.is_grounded is False
    assert body.drop_through_timer > 0.0
