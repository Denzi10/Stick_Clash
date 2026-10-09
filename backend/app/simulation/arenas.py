"""Arenas and Hazards for Stick Clash.
Implements the 8 launch arenas and dynamic hazards from Section 9.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from ..config import CANVAS_WIDTH, CANVAS_HEIGHT
from ..models.schemas import HazardSnapshot
from .physics import Platform, AABB


@dataclass
class ArenaHazard:
    id: str
    hazard_type: str  # spikes, lava, bounce_pad, conveyor, crusher, wind, falling_block
    x: float
    y: float
    width: float
    height: float
    damage: float = 0.0
    active: bool = True
    timer: float = 0.0
    period: float = 0.0
    push_x: float = 0.0
    push_y: float = 0.0
    warning: bool = False

    def update(self, dt: float) -> None:
        self.timer += dt
        if self.hazard_type == "lava_rising":
            # Lava rises 40 px every 20s and resets
            cycle = self.timer % 20.0
            if cycle < 10.0:
                rise = (cycle / 10.0) * 40.0
            else:
                rise = 40.0 - ((cycle - 10.0) / 10.0) * 40.0
            self.y = (CANVAS_HEIGHT - 30.0) - rise
            self.height = 30.0 + rise
        elif self.hazard_type == "crusher":
            # Crusher moves down every 6s, 1s warning
            cycle = self.timer % 6.0
            self.warning = (cycle >= 4.0 and cycle < 5.0)
            if cycle >= 5.0 and cycle < 5.5:
                self.active = True
                self.y = 200.0  # Slam down
            else:
                self.active = False
                self.y = 80.0   # Retracted
        elif self.hazard_type == "falling_block":
            # Falling stalactite / block
            cycle = self.timer % 8.0
            self.warning = (cycle >= 6.0 and cycle < 7.0)
            if cycle >= 7.0:
                self.active = True
                self.y += 600.0 * dt
                if self.y > CANVAS_HEIGHT - 60:
                    self.timer = 0.0
                    self.y = 80.0
                    self.active = False
            else:
                self.active = False
                self.y = 80.0


@dataclass
class ArenaDef:
    id: str
    name: str
    theme: str
    wrap_horizontal: bool
    platforms: List[Platform]
    hazards: List[ArenaHazard]
    player_spawns: List[Tuple[float, float]]
    weapon_spawns: List[Tuple[float, float, str]]
    background_theme: str


def build_arenas() -> Dict[str, ArenaDef]:
    arenas = {}

    # 1. Snow Peaks (Icy mountains, friction 0.3, wrap)
    arenas["snow_peaks"] = ArenaDef(
        id="snow_peaks",
        name="Snow Peaks",
        theme="Icy Mountains",
        wrap_horizontal=True,
        platforms=[
            # Ground tier
            Platform("sp_ground", 640, 680, 1100, 40, is_solid=True, is_slippery=True, friction=0.3),
            # Tier 1
            Platform("sp_t1_l", 280, 520, 300, 18, is_solid=False, is_slippery=True, friction=0.3),
            Platform("sp_t1_r", 1000, 520, 300, 18, is_solid=False, is_slippery=True, friction=0.3),
            # Tier 2
            Platform("sp_t2_c", 640, 360, 400, 18, is_solid=False, is_slippery=True, friction=0.3),
            # Tier 3
            Platform("sp_t3_l", 320, 210, 240, 18, is_solid=False, is_slippery=True, friction=0.3),
            Platform("sp_t3_r", 960, 210, 240, 18, is_solid=False, is_slippery=True, friction=0.3),
        ],
        hazards=[
            ArenaHazard("sp_spikes_l", "spikes", 120, 670, 80, 20, damage=15.0),
            ArenaHazard("sp_spikes_r", "spikes", 1160, 670, 80, 20, damage=15.0),
        ],
        player_spawns=[(280, 490), (1000, 490), (640, 330), (640, 640)],
        weapon_spawns=[(640, 330, "sword"), (320, 180, "bow"), (960, 180, "bat")],
        background_theme="snow",
    )

    # 2. Volcano Pit (Lava cavern, rising lava, no wrap)
    arenas["volcano_pit"] = ArenaDef(
        id="volcano_pit",
        name="Volcano Pit",
        theme="Lava Cavern",
        wrap_horizontal=False,
        platforms=[
            # Suspended platforms over lava
            Platform("vp_p_mid", 640, 620, 450, 24, is_solid=True),
            Platform("vp_t1_l", 240, 500, 260, 18, is_solid=False),
            Platform("vp_t1_r", 1040, 500, 260, 18, is_solid=False),
            Platform("vp_t2_l", 440, 350, 220, 18, is_solid=False),
            Platform("vp_t2_r", 840, 350, 220, 18, is_solid=False),
            Platform("vp_top", 640, 200, 320, 18, is_solid=False),
        ],
        hazards=[
            # Lava at bottom
            ArenaHazard("vp_lava", "lava_rising", 640, 700, 1280, 40, damage=8.0),
        ],
        player_spawns=[(240, 460), (1040, 460), (440, 310), (840, 310)],
        weapon_spawns=[(640, 170, "hammer"), (240, 460, "spear"), (1040, 460, "pistol")],
        background_theme="volcano",
    )

    # 3. Neon City (Rooftops, moving platforms, wrap)
    arenas["neon_city"] = ArenaDef(
        id="neon_city",
        name="Neon City",
        theme="Cyberpunk Rooftops",
        wrap_horizontal=True,
        platforms=[
            Platform("nc_bldg_l", 250, 640, 380, 160, is_solid=True),
            Platform("nc_bldg_r", 1030, 640, 380, 160, is_solid=True),
            # Moving middle platform
            Platform("nc_mov_mid", 640, 520, 240, 20, is_solid=False, is_moving=True, vx=100.0, path_min_x=450, path_max_x=830),
            Platform("nc_t2_l", 300, 360, 260, 18, is_solid=False),
            Platform("nc_t2_r", 980, 360, 260, 18, is_solid=False),
            Platform("nc_top", 640, 220, 300, 18, is_solid=False),
        ],
        hazards=[
            ArenaHazard("nc_neon_pad", "bounce_pad", 640, 710, 160, 20, push_y=-1000.0),
        ],
        player_spawns=[(250, 540), (1030, 540), (300, 320), (980, 320)],
        weapon_spawns=[(640, 190, "nunchucks"), (250, 530, "pistol"), (1030, 530, "boomerang")],
        background_theme="neon",
    )

    # 4. Jungle Ruins (Temple, bounce mushrooms, wrap)
    arenas["jungle_ruins"] = ArenaDef(
        id="jungle_ruins",
        name="Jungle Ruins",
        theme="Overgrown Temple",
        wrap_horizontal=True,
        platforms=[
            Platform("jr_floor", 640, 680, 1200, 40, is_solid=True),
            Platform("jr_t1_c", 640, 520, 360, 20, is_solid=False),
            Platform("jr_t1_l", 220, 420, 240, 18, is_solid=False),
            Platform("jr_t1_r", 1060, 420, 240, 18, is_solid=False),
            Platform("jr_t2_c", 640, 320, 420, 20, is_solid=False),
            Platform("jr_t3_top", 640, 160, 260, 18, is_solid=False),
        ],
        hazards=[
            ArenaHazard("jr_shroom_l", "bounce_pad", 100, 660, 60, 30, push_y=-1000.0),
            ArenaHazard("jr_shroom_r", "bounce_pad", 1180, 660, 60, 30, push_y=-1000.0),
        ],
        player_spawns=[(220, 380), (1060, 380), (640, 480), (640, 280)],
        weapon_spawns=[(640, 130, "spear"), (220, 380, "bat"), (1060, 380, "sword")],
        background_theme="jungle",
    )

    # 5. Sky Islands (Floating rocks, wind gusts, crumbling platforms, no wrap)
    arenas["sky_islands"] = ArenaDef(
        id="sky_islands",
        name="Sky Islands",
        theme="Floating Citadels",
        wrap_horizontal=False,
        platforms=[
            Platform("si_base_l", 300, 600, 340, 30, is_solid=True),
            Platform("si_base_r", 980, 600, 340, 30, is_solid=True),
            # Crumbling center platform
            Platform("si_crumb_mid", 640, 460, 220, 18, is_solid=False, is_crumbly=True),
            Platform("si_t2_l", 260, 340, 200, 18, is_solid=False),
            Platform("si_t2_r", 1020, 340, 200, 18, is_solid=False),
            Platform("si_top", 640, 220, 280, 18, is_solid=False),
        ],
        hazards=[
            ArenaHazard("si_wind", "wind", 640, 360, 1280, 720, push_x=150.0),
        ],
        player_spawns=[(300, 560), (980, 560), (260, 300), (1020, 300)],
        weapon_spawns=[(640, 190, "bow"), (300, 560, "boomerang"), (980, 560, "sword")],
        background_theme="sky",
    )

    # 6. Factory Floor (Conveyor belts, crushers, wrap)
    arenas["factory_floor"] = ArenaDef(
        id="factory_floor",
        name="Factory Floor",
        theme="Industrial Complex",
        wrap_horizontal=True,
        platforms=[
            Platform("ff_ground", 640, 680, 1160, 40, is_solid=True),
            Platform("ff_t1_l", 320, 510, 320, 20, is_solid=False),
            Platform("ff_t1_r", 960, 510, 320, 20, is_solid=False),
            Platform("ff_t2_c", 640, 360, 440, 20, is_solid=False),
            Platform("ff_top", 640, 200, 300, 18, is_solid=False),
        ],
        hazards=[
            # Conveyor moving at 120 px/s
            ArenaHazard("ff_conveyor", "conveyor", 640, 665, 400, 20, push_x=120.0),
            # Crusher with telegraph
            ArenaHazard("ff_crusher", "crusher", 640, 140, 120, 80, damage=30.0),
        ],
        player_spawns=[(320, 470), (960, 470), (640, 320), (320, 640)],
        weapon_spawns=[(640, 170, "hammer"), (320, 470, "nunchucks"), (960, 470, "pistol")],
        background_theme="factory",
    )

    # 7. Crystal Cave (Falling stalactites, no wrap)
    arenas["crystal_cave"] = ArenaDef(
        id="crystal_cave",
        name="Crystal Cave",
        theme="Subterranean Geode",
        wrap_horizontal=False,
        platforms=[
            Platform("cc_floor", 640, 670, 1200, 40, is_solid=True),
            Platform("cc_t1_l", 260, 510, 260, 20, is_solid=False),
            Platform("cc_t1_r", 1020, 510, 260, 20, is_solid=False),
            Platform("cc_t2_c", 640, 380, 380, 20, is_solid=False),
            Platform("cc_t3_l", 380, 230, 220, 18, is_solid=False),
            Platform("cc_t3_r", 900, 230, 220, 18, is_solid=False),
        ],
        hazards=[
            ArenaHazard("cc_stalactite_l", "falling_block", 440, 80, 40, 60, damage=20.0),
            ArenaHazard("cc_stalactite_r", "falling_block", 840, 80, 40, 60, damage=20.0),
        ],
        player_spawns=[(260, 470), (1020, 470), (640, 340), (640, 630)],
        weapon_spawns=[(640, 340, "sword"), (380, 190, "bow"), (900, 190, "hammer")],
        background_theme="cave",
    )

    # 8. Training Dojo (No hazards, clean symmetric layout)
    arenas["training_dojo"] = ArenaDef(
        id="training_dojo",
        name="Training Dojo",
        theme="Traditional Martial Arts Dojo",
        wrap_horizontal=False,
        platforms=[
            Platform("td_floor", 640, 660, 1160, 40, is_solid=True),
            Platform("td_t1_l", 320, 500, 280, 20, is_solid=False),
            Platform("td_t1_r", 960, 500, 280, 20, is_solid=False),
            Platform("td_t2_c", 640, 350, 400, 20, is_solid=False),
            Platform("td_top_l", 360, 200, 200, 18, is_solid=False),
            Platform("td_top_r", 920, 200, 200, 18, is_solid=False),
        ],
        hazards=[],
        player_spawns=[(320, 460), (960, 460), (440, 620), (840, 620)],
        weapon_spawns=[(640, 310, "sword"), (320, 460, "nunchucks"), (960, 460, "bat")],
        background_theme="dojo",
    )

    return arenas


class ArenaManager:
    def __init__(self, arena_id: str = "training_dojo"):
        self.all_arenas = build_arenas()
        self.current_arena = self.all_arenas.get(arena_id, self.all_arenas["training_dojo"])

    def set_arena(self, arena_id: str) -> None:
        if arena_id in self.all_arenas:
            self.current_arena = self.all_arenas[arena_id]

    def update(self, dt: float) -> None:
        for p in self.current_arena.platforms:
            p.update(dt)
        for h in self.current_arena.hazards:
            h.update(dt)

    def get_hazard_snapshots(self) -> List[HazardSnapshot]:
        return [
            HazardSnapshot(
                id=h.id,
                hazard_type=h.hazard_type,
                x=round(h.x, 1),
                y=round(h.y, 1),
                width=h.width,
                height=h.height,
                active=h.active,
                param=round(h.timer, 2),
            )
            for h in self.current_arena.hazards
        ]
