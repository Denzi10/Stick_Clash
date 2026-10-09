"""Status Effects System for Stick Clash.
Implements the 8 core status effects and diminishing returns logic.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from ..models.schemas import StatusType, StatusState


@dataclass
class ActiveStatus:
    status_type: StatusType
    duration: float
    remaining: float
    tick_rate: float = 1.0  # seconds per tick
    tick_timer: float = 0.0
    damage_per_tick: float = 0.0
    absorb_amount: float = 0.0  # For Shield status


class StatusManager:
    def __init__(self):
        self.statuses: Dict[StatusType, ActiveStatus] = {}
        # Freeze diminishing returns tracker: timestamps of previous freezes
        self.freeze_history: List[float] = []

    def apply_status(
        self,
        status_type: StatusType,
        custom_duration: Optional[float] = None,
        shield_amount: float = 30.0,
        current_time: float = 0.0,
    ) -> bool:
        # Freeze diminishing returns
        if status_type == StatusType.FREEZE:
            # Clean up freeze events older than 5 seconds
            self.freeze_history = [t for t in self.freeze_history if current_time - t <= 5.0]
            count = len(self.freeze_history)
            if count >= 2:
                # 3rd freeze within 5s is completely blocked
                return False
            duration = custom_duration or 1.5
            if count == 1:
                # 2nd freeze lasts half as long
                duration *= 0.5
            self.freeze_history.append(current_time)
        elif status_type == StatusType.BURN:
            duration = custom_duration or 4.0
        elif status_type == StatusType.POISON:
            duration = custom_duration or 6.0
        elif status_type == StatusType.SLOW:
            duration = custom_duration or 3.0
        elif status_type == StatusType.SHOCK:
            duration = custom_duration or 0.6
        elif status_type == StatusType.STUN:
            duration = custom_duration or 0.7
        elif status_type == StatusType.SHIELD:
            duration = custom_duration or 8.0
        elif status_type == StatusType.RAGE:
            duration = custom_duration or 8.0
        else:
            duration = custom_duration or 3.0

        dmg_per_tick = 0.0
        tick_rate = 1.0
        if status_type == StatusType.BURN:
            dmg_per_tick = 3.0
            tick_rate = 1.0
        elif status_type == StatusType.POISON:
            dmg_per_tick = 2.0
            tick_rate = 1.0

        absorb = shield_amount if status_type == StatusType.SHIELD else 0.0

        # Reapplication refreshes duration and resets tick timer
        self.statuses[status_type] = ActiveStatus(
            status_type=status_type,
            duration=duration,
            remaining=duration,
            tick_rate=tick_rate,
            tick_timer=0.0,
            damage_per_tick=dmg_per_tick,
            absorb_amount=absorb,
        )
        return True

    def remove_status(self, status_type: StatusType) -> None:
        if status_type in self.statuses:
            del self.statuses[status_type]

    def clear_all(self) -> None:
        self.statuses.clear()

    def has_status(self, status_type: StatusType) -> bool:
        return status_type in self.statuses

    def get_remaining(self, status_type: StatusType) -> float:
        st = self.statuses.get(status_type)
        return st.remaining if st else 0.0

    def reduce_freeze_time(self, amount: float = 0.4) -> None:
        """Called when user mashes jump while frozen to break out earlier."""
        if StatusType.FREEZE in self.statuses:
            self.statuses[StatusType.FREEZE].remaining = max(
                0.0, self.statuses[StatusType.FREEZE].remaining - amount
            )

    def absorb_damage(self, incoming_damage: float) -> Tuple[float, bool]:
        """Shield status absorbs damage before health. Returns (remaining_damage, shield_broke)."""
        if StatusType.SHIELD not in self.statuses:
            return incoming_damage, False

        shield = self.statuses[StatusType.SHIELD]
        if shield.absorb_amount >= incoming_damage:
            shield.absorb_amount -= incoming_damage
            if shield.absorb_amount <= 0:
                del self.statuses[StatusType.SHIELD]
                return 0.0, True
            return 0.0, False
        else:
            leftover = incoming_damage - shield.absorb_amount
            shield.absorb_amount = 0.0
            del self.statuses[StatusType.SHIELD]
            return leftover, True

    def update(self, dt: float) -> List[Tuple[StatusType, float]]:
        """Updates durations. Returns list of (status_type, damage_to_deal) for ticking dots."""
        expired = []
        tick_damages: List[Tuple[StatusType, float]] = []

        for st_type, st in list(self.statuses.items()):
            st.remaining -= dt
            if st.remaining <= 0.0:
                expired.append(st_type)
                continue

            if st.damage_per_tick > 0.0:
                st.tick_timer += dt
                if st.tick_timer >= st.tick_rate:
                    st.tick_timer -= st.tick_rate
                    tick_damages.append((st_type, st.damage_per_tick))

        for ex in expired:
            del self.statuses[ex]

        return tick_damages

    def to_snapshots(self) -> List[StatusState]:
        return [
            StatusState(
                status_type=st.status_type,
                remaining_secs=round(st.remaining, 2),
                total_secs=round(st.duration, 2),
                tick_timer=round(st.tick_timer, 2),
            )
            for st in self.statuses.values()
        ]
