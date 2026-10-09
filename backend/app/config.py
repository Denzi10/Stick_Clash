"""Stick Clash - Core Engine and Game Constants.
All values adhere directly to Stick Clash Project Specification v1.0.
"""

# Canvas Dimensions
CANVAS_WIDTH = 1280
CANVAS_HEIGHT = 720

# Network & Simulation Ticks
SIMULATION_HZ = 60          # 60 Hz server simulation tick
TICK_DT = 1.0 / SIMULATION_HZ
SNAPSHOT_HZ = 20            # Broadcast snapshots at 20 Hz
SNAPSHOT_INTERVAL_TICKS = SIMULATION_HZ // SNAPSHOT_HZ  # Every 3 ticks

# Movement Constants (Enhanced jump height & power attainment)
BASE_RUN_SPEED = 340.0        # px/s
GROUND_ACCEL = 3200.0         # px/s^2
AIR_CONTROL = 0.80            # 80% of ground control
GRAVITY = 2100.0              # px/s^2
JUMP_VELOCITY = -1080.0       # High-flying leap clearing all platform tiers
DOUBLE_JUMP_VELOCITY = -960.0 # Powerful double jump
MAX_FALL_SPEED = 1200.0       # px/s
FAST_FALL_SPEED = 1600.0      # px/s

# Hurtbox Dimensions
HURTBOX_WIDTH = 40.0
HURTBOX_HEIGHT = 90.0
HURTBOX_CROUCH_HEIGHT = 70.0

# Dash Constants
DASH_DISTANCE = 200.0       # px
DASH_DURATION = 0.16        # s
DASH_INVULN_DURATION = 0.12 # s
DASH_COOLDOWN = 1.0         # s
DASH_SPEED = DASH_DISTANCE / DASH_DURATION  # 1250 px/s

# Defense Constants
MAX_GUARD = 40.0
GUARD_REGEN_RATE = 15.0     # per second when not blocking
BLOCK_DAMAGE_REDUCTION = 0.70  # 70% damage reduction
BLOCK_KNOCKBACK_REDUCTION = 0.60  # 60% knockback reduction
GUARD_BREAK_STUN = 1.2      # s
PARRY_WINDOW_FRAMES = 8     # 8 frames (0.133s)
PARRY_WINDOW_SECS = PARRY_WINDOW_FRAMES / 60.0
PARRY_STUN_DURATION = 0.7   # s
PARRY_POWER_GAIN = 10.0

# Health & Power
DEFAULT_HEALTH = 100.0
RESPAWN_INVULN_SECS = 2.0
RESPAWN_DELAY_SECS = 3.0
MAX_POWER = 100.0
POWER_ON_RESPAWN = 25.0
SPECIAL_POWER_COST = 40.0         # was 50 (attain specials faster!)
SPECIAL_POWER_COST_RAGE = 15.0    # was 25
RAGE_POWER_COST = 100.0
RAGE_DURATION = 8.0               # s
RAGE_DAMAGE_BUFF = 0.35           # +35%
RAGE_SPEED_BUFF = 0.20            # +20%
RAGE_HEALTH_REGEN = 3.0           # HP/s
PASSIVE_POWER_REGEN = 2.5         # +2.5 power/s passively
DAMAGE_DEALT_POWER_MULT = 1.0     # 1 power per damage dealt (was 0.6)
DAMAGE_TAKEN_POWER_MULT = 0.8     # 0.8 power per damage taken (was 0.4)

# Disconnect Handling
DISCONNECT_HOLD_SECS = 20.0 # Wait 20s before bot takeover

# Room Code Alphabet (no look-alike characters)
ROOM_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
ROOM_CODE_LENGTH = 5
