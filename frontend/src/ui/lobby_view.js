/**
 * Lobby UI View: Room code sharing, class picker, bot management, and start match.
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

    if (this.startBtn) {
      this.startBtn.onclick = () => {
        this.socket.sendStartGame();
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

    this.classCards.forEach((card) => {
      card.onclick = () => {
        this.classCards.forEach((c) => c.classList.remove("active"));
        card.classList.add("active");
        this.selectedClass = card.dataset.class;
        // Notify socket
        if (this.socket.isConnected) {
          this.socket.send({
            type: "join",
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

    if (this.playersListEl) {
      this.playersListEl.innerHTML = "";
      data.players.forEach((p) => {
        const item = document.createElement("div");
        item.className = `lobby-player-row ${p.team === 0 ? "team-cyan" : "team-magenta"}`;
        item.innerHTML = `
          <div class="lobby-player-info">
            <span class="lobby-player-badge">${p.is_host ? "★ HOST" : (p.is_bot ? `🤖 BOT (${p.difficulty.toUpperCase()})` : "PLAYER")}</span>
            <span class="lobby-player-name">${p.nickname}</span>
          </div>
          <div class="lobby-player-class">${p.fighter_class.toUpperCase()}</div>
        `;
        this.playersListEl.appendChild(item);
      });
    }
  }
}
