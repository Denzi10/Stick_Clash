"""Unit tests for combat calculations, frame data, parry, block, and rage."""

import pytest
from app.simulation.combat import CombatState, calculate_hit, MOVE_TABLE
from app.simulation.physics import PhysicsBody
from app.models.schemas import FighterClass, StatusType
from app.config import (
    BLOCK_DAMAGE_REDUCTION,
    GUARD_BREAK_STUN,
    PARRY_POWER_GAIN,
    PARRY_STUN_DURATION,
)


def test_base_hit_damage():
    attacker = CombatState(FighterClass.BRAWLER)
    target = CombatState(FighterClass.BRAWLER)
    target_body = PhysicsBody()

    initial_hp = target.health
    res = calculate_hit(attacker, target, "light1", target_body, attacker_facing=1)

    assert res["type"] == "hit"
    assert res["damage"] == 5.0
    assert target.health == initial_hp - 5.0
    assert target_body.vx > 0  # Knocked away in facing direction


def test_bruiser_damage_mult():
    attacker = CombatState(FighterClass.BRUISER)  # 1.2x damage multiplier
    target = CombatState(FighterClass.BRAWLER)
    target_body = PhysicsBody()

    res = calculate_hit(attacker, target, "light1", target_body, attacker_facing=1)
    # 5.0 * 1.2 = 6.0
    assert res["damage"] == 6.0


def test_blocking_damage_reduction():
    attacker = CombatState(FighterClass.BRAWLER)
    target = CombatState(FighterClass.BRAWLER)
    target.start_block()
    target.block_held_time = 0.5  # Past parry window
    target_body = PhysicsBody()

    initial_guard = target.guard
    res = calculate_hit(attacker, target, "light1", target_body, attacker_facing=1)

    # 5.0 * (1 - 0.7) = 1.5
    assert res["damage"] == 1.5
    assert target.guard == initial_guard - 1.5


def test_parry_success():
    attacker = CombatState(FighterClass.BRAWLER)
    target = CombatState(FighterClass.BRAWLER)
    target.start_block()
    target.block_held_time = 0.05  # Within 8 frames parry window (<= 0.133s)
    target_body = PhysicsBody()

    initial_hp = target.health
    initial_power = target.power
    res = calculate_hit(attacker, target, "light1", target_body, attacker_facing=1)

    assert res["type"] == "parry"
    assert res["damage"] == 0.0
    assert target.health == initial_hp  # Negated damage
    assert attacker.stun_timer == PARRY_STUN_DURATION  # Attacker stunned
    assert target.power == initial_power + PARRY_POWER_GAIN  # Power rewarded


def test_guard_break_stun():
    attacker = CombatState(FighterClass.BRAWLER)
    target = CombatState(FighterClass.BRAWLER)
    target.guard = 1.0  # Almost depleted
    target.start_block()
    target.block_held_time = 0.5
    target_body = PhysicsBody()

    res = calculate_hit(attacker, target, "heavy", target_body, attacker_facing=1)
    assert target.guard == 0.0
    assert target.is_blocking is False
    assert target.stun_timer == GUARD_BREAK_STUN


def test_knockback_scaling_with_low_health():
    # Spec: Launch speed = base * (1 + 1.5 * (1 - hp/max_hp)) / weight
    attacker = CombatState(FighterClass.BRAWLER)
    target_full = CombatState(FighterClass.BRAWLER)
    body_full = PhysicsBody()
    calculate_hit(attacker, target_full, "light1", body_full, 1)

    target_low = CombatState(FighterClass.BRAWLER)
    target_low.health = 10.0  # 10% health
    body_low = PhysicsBody()
    calculate_hit(attacker, target_low, "light1", body_low, 1)

    assert body_low.vx > body_full.vx  # Much higher knockback at low health


def test_rage_activation_and_buff():
    combat = CombatState(FighterClass.BRAWLER)
    combat.power = 100.0
    assert combat.trigger_rage() is True
    assert combat.is_in_rage is True
    assert combat.power == 0.0

    # Cannot re-activate while already in rage
    assert combat.trigger_rage() is False
