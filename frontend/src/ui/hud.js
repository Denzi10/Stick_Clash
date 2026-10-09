/**
 * In-Game HUD overlay updater (Health, Guard, Power, Kill Feed, Objectives).
 */

export class HUD {
  constructor() {
    this.timerEl = document.getElementById("hud-match-timer");
    this.objectiveEl = document.getElementById("hud-objective-text");
    this.killFeedEl = document.getElementById("hud-kill-feed");
    this.p1PlateEl = document.getElementById("hud-p1-plate");
    this.p2PlateEl = document.getElementById("hud-p2-plate");
    this.p3PlateEl = document.getElementById("hud-p3-plate");
    this.p4PlateEl = document.getElementById("hud-p4-plate");
    this.plates = [this.p1PlateEl, this.p2PlateEl, this.p3PlateEl, this.p4PlateEl];
  }

  update(snapshot, localPlayerId) {
    if (!snapshot) return;

    // 1. Match Timer
    if (this.timerEl) {
      const mins = Math.floor(snapshot.match_time_remaining / 60);
      const secs = Math.floor(snapshot.match_time_remaining % 60);
      this.timerEl.innerText = `${mins}:${secs < 10 ? "0" : ""}${secs}`;
    }

    // 2. Objective Tracker
    if (this.objectiveEl && snapshot.objective_info) {
      const obj = snapshot.objective_info;
      if (snapshot.mode === "duel") {
        this.objectiveEl.innerText = `ROUND ${obj.round || 1} / ${obj.max_rounds || 3}`;
      } else if (snapshot.mode === "team_clash") {
        const t0 = obj.team_kills ? obj.team_kills[0] || 0 : 0;
        const t1 = obj.team_kills ? obj.team_kills[1] || 0 : 0;
        this.objectiveEl.innerText = `TEAM CYAN: ${t0}  |  TEAM MAGENTA: ${t1}  (TARGET: ${obj.target_kills})`;
      } else if (snapshot.mode === "gauntlet") {
        this.objectiveEl.innerText = `LEVEL ${obj.level || 1} - ${String(obj.objective || "").toUpperCase().replace(/_/g, " ")}`;
      } else {
        this.objectiveEl.innerText = `FIRST TO ${obj.target_kills || 15} KILLS`;
      }
    }

    // 3. Player Plates
    snapshot.players.forEach((p, idx) => {
      const plate = this.plates[idx];
      if (!plate) return;

      plate.style.display = "flex";
      const nameEl = plate.querySelector(".hud-name");
      const hpBar = plate.querySelector(".hud-hp-bar");
      const guardBar = plate.querySelector(".hud-guard-bar");
      const powerBar = plate.querySelector(".hud-power-bar");
      const ragePrompt = plate.querySelector(".hud-rage-prompt");
      const weaponEl = plate.querySelector(".hud-weapon-badge");

      if (nameEl) {
        nameEl.innerText = `${p.nickname} [${p.fighter_class.toUpperCase()}]`;
        nameEl.style.color = p.team === 0 ? "#00f0ff" : "#ff0055";
      }

      if (hpBar) {
        const hpPct = Math.max(0, Math.min(100, (p.health / p.max_health) * 100));
        hpBar.style.width = `${hpPct}%`;
      }

      if (guardBar) {
        const guardPct = Math.max(0, Math.min(100, (p.guard / p.max_guard) * 100));
        guardBar.style.width = `${guardPct}%`;
      }

      if (powerBar) {
        const powPct = Math.max(0, Math.min(100, (p.power / 100.0) * 100));
        powerBar.style.width = `${powPct}%`;
      }

      if (ragePrompt) {
        ragePrompt.style.display = p.power >= 100 ? "block" : "none";
      }

      if (weaponEl) {
        if (p.held_weapon) {
          weaponEl.style.display = "block";
          weaponEl.innerText = `⚔ ${p.held_weapon.weapon_type.toUpperCase()} (${p.held_weapon.durability})`;
        } else {
          weaponEl.style.display = "none";
        }
      }
    });

    // Hide extra plates
    for (let i = snapshot.players.length; i < 4; i++) {
      if (this.plates[i]) this.plates[i].style.display = "none";
    }
  }

  addKillFeedEntry(victimName, killerName, isHazard = false) {
    if (!this.killFeedEl) return;
    const item = document.createElement("div");
    item.className = "kill-feed-item";
    if (killerName) {
      item.innerHTML = `<span class="kf-killer">${killerName}</span> ⚔ <span class="kf-victim">${victimName}</span>`;
    } else {
      item.innerHTML = `☠ <span class="kf-victim">${victimName}</span> was eliminated`;
    }
    this.killFeedEl.appendChild(item);
    setTimeout(() => {
      item.remove();
    }, 4500);
  }
}
