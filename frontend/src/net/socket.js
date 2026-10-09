/**
 * WebSocket Network Client for Stick Clash.
 * Handles room connectivity, inputs streaming, and snapshot dispatching.
 */

export class GameSocket {
  constructor() {
    this.ws = null;
    this.roomCode = null;
    this.playerId = null;
    this.isConnected = false;
    this.onLobbyUpdate = null;
    this.onGameStarted = null;
    this.onSnapshot = null;
    this.onEmote = null;
    this.onError = null;
    this.seq = 0;
  }

  connect(roomCode, playerId, nickname, fighterClass, team = 0) {
    this.roomCode = roomCode.toUpperCase().trim();
    this.playerId = playerId;

    // Determine host protocol
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws/${this.roomCode}`;

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      this.isConnected = true;
      // Send join
      this.send({
        type: "join",
        player_id: this.playerId,
        nickname: nickname,
        fighter_class: fighterClass,
        team: team,
      });
    };

    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "lobby_update" && this.onLobbyUpdate) {
          this.onLobbyUpdate(msg);
        } else if (msg.type === "game_started" && this.onGameStarted) {
          this.onGameStarted(msg);
        } else if (msg.type === "snapshot" && this.onSnapshot) {
          this.onSnapshot(msg.data);
        } else if (msg.type === "emote" && this.onEmote) {
          this.onEmote(msg);
        }
      } catch (err) {
        console.error("Failed to parse websocket message", err);
      }
    };

    this.ws.onclose = () => {
      this.isConnected = false;
    };

    this.ws.onerror = (err) => {
      console.error("WebSocket error:", err);
      if (this.onError) this.onError(err);
    };
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  sendInput(bitmask) {
    this.seq++;
    this.send({
      type: "input",
      bitmask: bitmask,
      seq: this.seq,
    });
  }

  sendStartGame() {
    this.send({ type: "start_game" });
  }

  sendAddBot(difficulty = "normal", fighterClass = "brawler") {
    this.send({
      type: "add_bot",
      difficulty: difficulty,
      fighter_class: fighterClass,
    });
  }

  sendSelectUpgrade(upgradeId) {
    this.send({
      type: "select_upgrade",
      upgrade_id: upgradeId,
    });
  }

  sendEmote(emoteId) {
    this.send({
      type: "emote",
      emote_id: emoteId,
    });
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnected = false;
  }
}

export const gameSocket = new GameSocket();
