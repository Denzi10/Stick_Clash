/**
 * Stick Clash - Main Game Coordinator & Entry Point.
 */

import { gameSocket } from "./net/socket.js";
import { inputManager } from "./input/input_manager.js";
import { soundFx } from "./audio/sound_fx.js";
import { StickmanRenderer } from "./render/stickman.js";
import { ParticleSystem } from "./render/particles.js";
import { ArenaView } from "./render/arena_view.js";
import { HUD } from "./ui/hud.js";
import { LobbyView } from "./ui/lobby_view.js";
import { UpgradeModal } from "./ui/upgrade_modal.js";

class StickClashGame {
  constructor() {
    this.canvas = document.getElementById("game-canvas");
    this.ctx = this.canvas.getContext("2d");

    // Subsystems
    this.stickmanRenderer = new StickmanRenderer();
    this.particleSystem = new ParticleSystem();
    this.arenaView = new ArenaView();
    this.hud = new HUD();
    this.lobbyView = new LobbyView(gameSocket);
    this.upgradeModal = new UpgradeModal(gameSocket);

    // State
    this.currentScreen = "title"; // title, lobby, game, results
    this.latestSnapshot = null;
    this.localPlayerId = "player_" + Math.floor(Math.random() * 9000 + 1000);
    this.nickname = "Player " + this.localPlayerId.slice(-3);
    this.platforms = [];

    // Screen DOM Elements
    this.screenTitle = document.getElementById("screen-title");
    this.screenLobby = document.getElementById("screen-lobby");
    this.inGameHud = document.getElementById("in-game-hud");
    this.screenResults = document.getElementById("screen-results");
    this.screenTutorial = document.getElementById("screen-tutorial");

    this.setupEvents();
    this.setupNetwork();
    this.checkUrlForRoomCode();

    // Start 60 FPS animation loop
    this.lastTime = performance.now();
    requestAnimationFrame((t) => this.loop(t));
  }

  setupEvents() {
    // Title Buttons
    document.getElementById("btn-quick-match").onclick = () => {
      soundFx.init();
      soundFx.playClick();
      this.quickMatch();
    };

    document.getElementById("btn-create-room").onclick = () => {
      soundFx.init();
      soundFx.playClick();
      this.createRoom();
    };

    document.getElementById("btn-join-code").onclick = () => {
      soundFx.init();
      soundFx.playClick();
      const codeInput = document.getElementById("input-room-code");
      const code = (codeInput.value || "").trim().toUpperCase();
      if (code) {
        this.joinRoom(code);
      }
    };

    document.getElementById("btn-open-tutorial").onclick = () => {
      soundFx.playClick();
      this.screenTutorial.style.display = "flex";
    };

    document.getElementById("btn-close-tutorial").onclick = () => {
      soundFx.playClick();
      this.screenTutorial.style.display = "none";
    };

    document.getElementById("btn-toggle-music").onclick = () => {
      soundFx.init();
      soundFx.toggleMusic();
    };

    document.getElementById("btn-return-lobby").onclick = () => {
      soundFx.playClick();
      this.showScreen("lobby");
    };
  }

  setupNetwork() {
    gameSocket.onLobbyUpdate = (data) => {
      this.lobbyView.renderLobby(data);
      if (this.currentScreen !== "game") {
        this.showScreen("lobby");
      }
    };

    gameSocket.onGameStarted = (data) => {
      soundFx.playClick();
      this.showScreen("game");
    };

    gameSocket.onSnapshot = (snapshot) => {
      this.processSnapshotEvents(snapshot);
      this.latestSnapshot = snapshot;
      this.hud.update(snapshot, this.localPlayerId);

      // Check game over
      if (snapshot.is_game_over && this.currentScreen === "game") {
        this.showResults(snapshot);
      }
    };
  }

  checkUrlForRoomCode() {
    const params = new URLSearchParams(window.location.search);
    const roomParam = params.get("room") || params.get("code");
    if (roomParam) {
      const code = roomParam.trim().toUpperCase();
      document.getElementById("input-room-code").value = code;
      // Auto-join
      setTimeout(() => {
        this.joinRoom(code);
      }, 300);
    }
  }

  async quickMatch() {
    try {
      const res = await fetch("/api/rooms");
      const rooms = await res.json();
      const openRoom = rooms.find((r) => !r.in_game && r.players_count < r.max_players);
      if (openRoom) {
        this.joinRoom(openRoom.room_code);
      } else {
        this.createRoom();
      }
    } catch (err) {
      this.createRoom();
    }
  }

  async createRoom() {
    try {
      const res = await fetch("/api/rooms/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode: "duel", arena_id: "training_dojo", max_players: 4 }),
      });
      const data = await res.json();
      this.joinRoom(data.room_code);
    } catch (err) {
      console.error("Failed to create room via REST, falling back to direct join", err);
      const code = Math.random().toString(36).substring(2, 7).toUpperCase();
      this.joinRoom(code);
    }
  }

  joinRoom(code) {
    gameSocket.connect(
      code,
      this.localPlayerId,
      this.nickname,
      this.lobbyView.selectedClass,
      0
    );
  }

  showScreen(screen) {
    this.currentScreen = screen;
    this.screenTitle.style.display = screen === "title" ? "flex" : "none";
    this.screenLobby.style.display = screen === "lobby" ? "flex" : "none";
    this.inGameHud.style.display = screen === "game" ? "block" : "none";
    this.screenResults.style.display = screen === "results" ? "flex" : "none";
  }

  showResults(snapshot) {
    this.showScreen("results");
    const titleEl = document.getElementById("results-title");
    const winnerEl = document.getElementById("results-winner");

    if (snapshot.winning_team !== null) {
      const teamName = snapshot.winning_team === 0 ? "TEAM CYAN" : "TEAM MAGENTA";
      titleEl.innerText = `${teamName} WINS!`;
      winnerEl.innerText = "Congratulations on victory!";
    } else if (snapshot.winner_id) {
      const winner = snapshot.players.find((p) => p.id === snapshot.winner_id);
      titleEl.innerText = `${winner ? winner.nickname : "CHAMPION"} WINS!`;
      winnerEl.innerText = "Victory attained!";
    } else {
      titleEl.innerText = "MATCH CONCLUDED";
      winnerEl.innerText = "Time limit expired.";
    }
    soundFx.playKO();
  }

  processSnapshotEvents(snapshot) {
    if (!snapshot.events) return;
    for (const ev of snapshot.events) {
      if (ev.event_type === "hit") {
        soundFx.playPunch(ev.data.damage > 10);
        this.particleSystem.spawnHitSparks(ev.data.x, ev.data.y, "#ffea00", 14);
        this.particleSystem.spawnDamageText(ev.data.x, ev.data.y, ev.data.damage, ev.data.damage > 12);
      } else if (ev.event_type === "parry") {
        soundFx.playParry();
        const defender = snapshot.players.find((p) => p.id === ev.data.defender_id);
        if (defender) {
          this.particleSystem.spawnParryRing(defender.x, defender.y - 45);
        }
      } else if (ev.event_type === "ko") {
        soundFx.playKO();
        const victim = snapshot.players.find((p) => p.id === ev.data.victim_id);
        const killer = snapshot.players.find((p) => p.id === ev.data.killer_id);
        const vName = victim ? victim.nickname : "Player";
        const kName = killer ? killer.nickname : null;
        this.hud.addKillFeedEntry(vName, kName, !kName);
      }
    }
  }

  loop(currentTime) {
    const dt = Math.min(0.1, (currentTime - this.lastTime) / 1000.0);
    this.lastTime = currentTime;
    const now = currentTime / 1000.0;

    // 1. Send inputs if in game
    if (this.currentScreen === "game" && gameSocket.isConnected) {
      const bitmask = inputManager.getBitmask();
      gameSocket.sendInput(bitmask);

      // Audio triggers on dash
      if (bitmask & (1 << 7)) {
        // Dash sound
        // Throttled in soundFx
      }
    }

    // 2. Render 60 FPS
    this.render(now, dt);

    requestAnimationFrame((t) => this.loop(t));
  }

  render(now, dt) {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, 1280, 720);

    // Apply screen shake
    ctx.save();
    if (this.particleSystem.screenShake > 0) {
      const shakeX = (Math.random() - 0.5) * this.particleSystem.screenShake * 2;
      const shakeY = (Math.random() - 0.5) * this.particleSystem.screenShake * 2;
      ctx.translate(shakeX, shakeY);
    }

    const arenaTheme = this.latestSnapshot ? this.latestSnapshot.arena_id : "training_dojo";

    // 1. Background Parallax
    this.arenaView.renderBackground(ctx, arenaTheme, now);

    // 2. Hazards
    if (this.latestSnapshot && this.latestSnapshot.hazards) {
      this.arenaView.renderHazards(ctx, this.latestSnapshot.hazards, now);
    }

    // Default ground line if no snapshot
    ctx.strokeStyle = "#3b82f6";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(0, 680);
    ctx.lineTo(1280, 680);
    ctx.stroke();

    // 3. Pickups & Projectiles
    if (this.latestSnapshot) {
      if (this.latestSnapshot.pickups) {
        this.arenaView.renderPickups(ctx, this.latestSnapshot.pickups, now);
      }
      if (this.latestSnapshot.projectiles) {
        this.arenaView.renderProjectiles(ctx, this.latestSnapshot.projectiles);
      }

      // 4. Players
      for (const p of this.latestSnapshot.players) {
        this.stickmanRenderer.render(ctx, p, now);
      }
    }

    // 5. Particles & Visual FX
    this.particleSystem.update(dt);
    this.particleSystem.render(ctx);

    ctx.restore();
  }
}

window.addEventListener("DOMContentLoaded", () => {
  new StickClashGame();
});
