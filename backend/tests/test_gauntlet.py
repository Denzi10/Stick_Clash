"""Unit tests for Gauntlet mode, upgrades pool, and objective tracking."""

import pytest
from app.modes.gauntlet import GauntletMode, UPGRADES_POOL
from app.rooms.room import PlayerEntity
from app.models.schemas import FighterClass


def test_gauntlet_upgrade_selection():
    mode = GauntletMode()
    p1 = PlayerEntity("p1", "Tester", FighterClass.BRAWLER)

    mode.generate_upgrade_offers([p1])
    assert "p1" in mode.pending_offers
    offers = mode.pending_offers["p1"]
    assert len(offers) == 3

    chosen_id = offers[0].id
    assert mode.select_upgrade("p1", chosen_id) is True
    assert mode.player_upgrades["p1"][chosen_id] == 1
    assert "p1" not in mode.pending_offers


def test_gauntlet_boss_level_on_5():
    mode = GauntletMode()
    mode.current_level = 5
    mode.setup_level()

    assert mode.current_objective == "boss"
    assert mode.boss_active is True
    assert mode.boss_health == 1200.0
