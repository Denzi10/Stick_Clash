"""Unit tests for Room Manager, 5-char room codes, and assist tracking."""

import pytest
from app.rooms.manager import RoomManager
from app.modes.base_mode import BaseMode
from app.modes.free_for_all import FreeForAllMode
from app.models.schemas import GameMode, FighterClass
from app.config import ROOM_CODE_ALPHABET, ROOM_CODE_LENGTH


def test_room_code_generation():
    rm = RoomManager()
    code = rm.generate_code()
    assert len(code) == ROOM_CODE_LENGTH
    for ch in code:
        assert ch in ROOM_CODE_ALPHABET


def test_room_creation_and_quick_match():
    rm = RoomManager()
    room1 = rm.create_room(mode=GameMode.DUEL)
    assert room1.room_code in rm.rooms

    # Quick match should find this room
    qm_room = rm.quick_match()
    assert qm_room is not None


def test_kill_and_assist_5s_window():
    mode = FreeForAllMode()
    t = 100.0

    # Attacker 1 hits victim at t=97.0
    mode.register_damage("p1", "victim", 20.0, current_time=97.0)
    # Attacker 2 hits victim at t=99.0
    mode.register_damage("p2", "victim", 30.0, current_time=99.0)

    killer, assist = mode.process_kill("victim", killer_id=None, current_time=100.0)

    # Last damager within 5s is p2, second damager is p1
    assert killer == "p2"
    assert assist == "p1"
    assert mode.player_kills["p2"] == 1
    assert mode.player_assists["p1"] == 1
    assert mode.player_scores["p2"] == 100
    assert mode.player_scores["p1"] == 25
