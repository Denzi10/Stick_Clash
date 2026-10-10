/**
 * Lobby UI View: Room code sharing, class picker, game mode, arena theme, bot management, and start match.
 */

export class LobbyView {
  constructor(socket) {
    this.socket = socket;
    this.roomCodeEl = document.getElementById("lobby-room-code");
    this.copyCodeBtn = document.getElementById("btn-copy-code");
    this.copyLinkBtn = document.getElementById("btn-copy-link");
    this.playersListEl = document.getElementById("lobby-players-list");
    this.startBtn = document.getElementById("btn-start-match");
    this.addBotBtn = document.getElementById("btn-add-bot");
    this.modeSelect = document.getElementById("select-game-mode");
    this.arenaSelect = document.getElementById("select-arena-theme");
    this.botDiffSelect = document.getElementById("select-bot-difficulty");
    this.classCards = document.querySelectorAll(".class-select-card");

    this.selectedClass = "brawler";
    this.selectedTeam = 0;
    this.isHost = false;

    this.setupEvents();
  }

  setupEvents() {
    if (this.copyCodeBtn) {
      this.copyCodeBtn.onclick = () => {
        const code = this.roomCodeEl.innerText;
        navigator.clipboard.writeText(code);
        this.copyCodeBtn.innerText = "COPIED!";
        setTimeout(() => (this.copyCodeBtn.innerText = "COPY CODE"), 2000);
      };
    }

    if (this.copyLinkBtn) {
      this.copyLinkBtn.onclick = () => {
        const code = this.roomCodeEl.innerText;
        const url = `${window.location.origin}/?room=${code}`;
        navigator.clipboard.writeText(url);
        this.copyLinkBtn.innerText = "LINK COPIED!";
        setTimeout(() => (this.copyLinkBtn.innerText = "SHARE LINK"), 2000);
      };
    }

    if (this.modeSelect) {
      this.modeSelect.onchange = () => {
        if (this.isHost && this.socket.isConnected) {
          this.socket.send({
            type: "set_mode",
            mode: this.modeSelect.value,
            arena_id: this.arenaSelect ? this.arenaSelect.value : "space_altar",
          });
        }
      };
    }

    if (this.arenaSelect) {
      this.arenaSelect.onchange = () => {
        if (this.isHost && this.socket.isConnected) {
          this.socket.send({
            type: "set_mode",
            mode: this.modeSelect ? this.modeSelect.value : "duel",
            arena_id: this.arenaSelect.value,
          });
        }
      };
    }

    if (this.startBtn) {
      this.startBtn.onclick = () => {
        const diff = this.botDiffSelect ? this.botDiffSelect.value : "normal";
        const mode = this.modeSelect ? this.modeSelect.value : "duel";
        const arena = this.arenaSelect ? this.arenaSelect.value : "random";
        // Notify host selections before start
        if (this.socket.isConnected) {
          this.socket.send({
            type: "set_mode",
            mode: mode,
            arena_id: arena,
          });
          this.socket.sendStartGame(diff);
        }
      };
    }

    if (this.addBotBtn) {
      this.addBotBtn.onclick = () => {
        const diff = this.botDiffSelect ? this.botDiffSelect.value : "normal";
        const classes = ["brawler", "ninja", "mage", "bruiser"];
        const randClass = classes[Math.floor(Math.random() * classes.length)];
        this.socket.sendAddBot(diff, randClass);
      };
    }

    // Fighter Class Selection - works for ALL modes
    this.classCards.forEach((card) => {
      card.onclick = () => {
        this.classCards.forEach((c) => c.classList.remove("active"));
        card.classList.add("active");
        this.selectedClass = card.dataset.class;

        // Send class change to server
        if (this.socket.isConnected) {
          this.socket.send({
            type: "select_class",
            player_id: this.socket.playerId,
            fighter_class: this.selectedClass,
            team: this.selectedTeam,
          });
        }
      };
    });
  }

  renderLobby(data) {
    if (this.roomCodeEl) {
      this.roomCodeEl.innerText = data.room_code;
    }

    this.isHost = data.host_id === this.socket.playerId;
    if (this.startBtn) {
      this.startBtn.style.display = this.isHost ? "block" : "none";
    }
    if (this.addBotBtn) {
      this.addBotBtn.style.display = this.isHost ? "block" : "none";
    }
    if (this.modeSelect) {
      this.modeSelect.disabled = !this.isHost;
      if (data.mode) {
        this.modeSelect.value = data.mode;
      }
    }
    if (this.arenaSelect) {
      this.arenaSelect.disabled = !this.isHost;
      if (data.arena_id) {
        this.arenaSelect.value = data.arena_id;
      }
    }

    // Sync selected class card with current player state
    const me = data.players.find((p) => p.id === this.socket.playerId);
    if (me && me.fighter_class) {
      this.selectedClass = me.fighter_class;
      this.classCards.forEach((c) => {
        if (c.dataset.class === me.fighter_class) {
          c.classList.add("active");
        } else {
          c.classList.remove("active");
        }
      });
    }

    if (this.playersListEl) {
      this.playersListEl.innerHTML = "";
      data.players.forEach((p) => {
        const item = document.createElement("div");
        item.className = `lobby-player-row ${p.team === 0 ? "team-cyan" : "team-magenta"}`;

        const classBadgeColors = {
          brawler: "#00f0ff",
          ninja: "#a855f7",
          mage: "#38bdf8",
          bruiser: "#ff0055",
        };
        const classColor = classBadgeColors[p.fighter_class] || "#00f0ff";

        item.innerHTML = `
          <div class="lobby-player-info">
            <span class="lobby-player-badge">${p.is_host ? "★ HOST" : (p.is_bot ? `🤖 BOT (${p.difficulty.toUpperCase()})` : "PLAYER")}</span>
            <span class="lobby-player-name">${p.nickname}</span>
          </div>
          <div class="lobby-player-class" style="border: 1px solid ${classColor}; padding: 3px 8px; border-radius: 5px; color: ${classColor}; font-weight: 700; background: rgba(0,0,0,0.4)">
            ${p.fighter_class.toUpperCase()}
          </div>
        `;
        this.playersListEl.appendChild(item);
      });
    }
  }
}
