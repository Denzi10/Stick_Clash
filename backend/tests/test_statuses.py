"""Unit tests for the 8 Status Effects and Diminishing Returns."""

import pytest
from app.simulation.statuses import StatusManager
from app.models.schemas import StatusType


def test_status_tick_damage():
    sm = StatusManager()
    sm.apply_status(StatusType.BURN, custom_duration=4.0)

    # 1 second of simulation
    ticks = sm.update(1.0)
    assert len(ticks) == 1
    assert ticks[0][0] == StatusType.BURN
    assert ticks[0][1] == 3.0  # 3 dmg per second


def test_freeze_diminishing_returns():
    sm = StatusManager()
    # 1st freeze at t=0
    assert sm.apply_status(StatusType.FREEZE, current_time=0.0) is True
    assert sm.get_remaining(StatusType.FREEZE) == 1.5

    # Clear and 2nd freeze within 5s at t=2.0
    sm.clear_all()
    assert sm.apply_status(StatusType.FREEZE, current_time=2.0) is True
    # 2nd freeze duration is halved (0.75s)
    assert sm.get_remaining(StatusType.FREEZE) == 0.75

    # Clear and 3rd freeze within 5s at t=3.0
    sm.clear_all()
    # 3rd freeze is completely blocked!
    assert sm.apply_status(StatusType.FREEZE, current_time=3.0) is False
    assert sm.has_status(StatusType.FREEZE) is False


def test_shield_damage_absorption():
    sm = StatusManager()
    sm.apply_status(StatusType.SHIELD, shield_amount=30.0)

    # Incoming hit of 10 dmg
    leftover, broke = sm.absorb_damage(10.0)
    assert leftover == 0.0
    assert broke is False
    assert sm.has_status(StatusType.SHIELD) is True

    # Incoming hit of 25 dmg (remaining shield is 20)
    leftover2, broke2 = sm.absorb_damage(25.0)
    assert leftover2 == 5.0
    assert broke2 is True
    assert sm.has_status(StatusType.SHIELD) is False
