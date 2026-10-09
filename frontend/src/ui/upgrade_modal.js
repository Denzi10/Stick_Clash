/**
 * Gauntlet 3-Card Upgrade Modal for Stick Clash.
 */

export class UpgradeModal {
  constructor(socket) {
    this.socket = socket;
    this.modalEl = document.getElementById("modal-upgrades");
    this.cardsContainer = document.getElementById("upgrade-cards-container");
    this.timerBar = document.getElementById("upgrade-timer-bar");
    this.timerText = document.getElementById("upgrade-timer-text");
  }

  showOffers(offers, totalTime = 10.0) {
    if (!this.modalEl || !this.cardsContainer) return;
    this.cardsContainer.innerHTML = "";
    this.modalEl.style.display = "flex";

    offers.forEach((u) => {
      const card = document.createElement("div");
      card.className = "upgrade-card";
      card.innerHTML = `
        <div class="upgrade-card-icon">⚡</div>
        <div class="upgrade-card-title">${u.name}</div>
        <div class="upgrade-card-desc">${u.description}</div>
        <div class="upgrade-card-stacks">Stacks: ${u.current_stacks} / ${u.max_stacks}</div>
        <button class="btn-select-upgrade">CHOOSE</button>
      `;
      card.onclick = () => {
        this.socket.sendSelectUpgrade(u.id);
        this.hide();
      };
      this.cardsContainer.appendChild(card);
    });
  }

  hide() {
    if (this.modalEl) {
      this.modalEl.style.display = "none";
    }
  }
}
