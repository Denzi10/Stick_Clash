/**
 * Particle and Visual FX Engine for Stick Clash.
 * Handles impacts, ink splatters, elemental effects, dash trails, and floating text.
 */

export class ParticleSystem {
  constructor() {
    this.particles = [];
    this.floatingTexts = [];
    this.screenShake = 0.0;
    this.shakeDecay = 0.9;
  }

  addScreenShake(intensity) {
    this.screenShake = Math.max(this.screenShake, intensity);
  }

  update(dt) {
    // Screen shake decay
    if (this.screenShake > 0.1) {
      this.screenShake *= Math.pow(this.shakeDecay, dt * 60);
    } else {
      this.screenShake = 0.0;
    }

    // Update particles
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.life -= dt;
      if (p.life <= 0) {
        this.particles.splice(i, 1);
        continue;
      }
      p.x += p.vx * dt;
      p.y += p.vy * dt;
      if (p.gravity) p.vy += p.gravity * dt;
    }

    // Update floating texts
    for (let i = this.floatingTexts.length - 1; i >= 0; i--) {
      const ft = this.floatingTexts[i];
      ft.life -= dt;
      if (ft.life <= 0) {
        this.floatingTexts.splice(i, 1);
        continue;
      }
      ft.y += ft.vy * dt;
      ft.scale = Math.min(1.4, ft.scale + dt * 2.0);
    }
  }

  render(ctx) {
    // Render particles
    for (const p of this.particles) {
      const alpha = Math.max(0, p.life / p.maxLife);
      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.fillStyle = p.color;
      ctx.shadowColor = p.color;
      ctx.shadowBlur = p.glow ? 8 : 0;

      if (p.shape === "spark") {
        ctx.fillRect(p.x - p.size / 2, p.y - p.size / 2, p.size, p.size);
      } else if (p.shape === "splatter") {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
      } else if (p.shape === "ring") {
        ctx.strokeStyle = p.color;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(p.x, p.y, (1.0 - alpha) * p.size, 0, Math.PI * 2);
        ctx.stroke();
      }
      ctx.restore();
    }

    // Render floating damage numbers
    for (const ft of this.floatingTexts) {
      const alpha = Math.max(0, ft.life / ft.maxLife);
      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.font = `bold ${Math.round(20 * ft.scale)}px 'Orbitron', sans-serif`;
      ctx.fillStyle = ft.color;
      ctx.strokeStyle = "#000000";
      ctx.lineWidth = 3;
      ctx.strokeText(ft.text, ft.x, ft.y);
      ctx.fillText(ft.text, ft.x, ft.y);
      ctx.restore();
    }
  }

  spawnHitSparks(x, y, color = "#ffea00", count = 12) {
    this.addScreenShake(6.0);
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 150 + Math.random() * 350;
      this.particles.push({
        x,
        y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        size: 2 + Math.random() * 4,
        color,
        life: 0.2 + Math.random() * 0.25,
        maxLife: 0.45,
        gravity: 300,
        shape: "spark",
        glow: true,
      });
    }

    // Ink splatter burst (stylized doodle blood-free ink)
    for (let i = 0; i < 6; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 40 + Math.random() * 120;
      this.particles.push({
        x: x + (Math.random() - 0.5) * 10,
        y: y + (Math.random() - 0.5) * 10,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        size: 3 + Math.random() * 5,
        color: "#0f172a",
        life: 0.35 + Math.random() * 0.2,
        maxLife: 0.55,
        gravity: 500,
        shape: "splatter",
        glow: false,
      });
    }
  }

  spawnDashTrail(x, y, facing, color = "#00f0ff") {
    for (let i = 0; i < 4; i++) {
      this.particles.push({
        x: x - facing * (i * 12),
        y: y - 45 + (Math.random() - 0.5) * 30,
        vx: -facing * 40,
        vy: (Math.random() - 0.5) * 20,
        size: 4 + Math.random() * 6,
        color,
        life: 0.18,
        maxLife: 0.18,
        gravity: 0,
        shape: "splatter",
        glow: true,
      });
    }
  }

  spawnDamageText(x, y, text, isCrit = false) {
    this.floatingTexts.push({
      x: x + (Math.random() - 0.5) * 20,
      y: y - 20,
      vy: -60,
      text: String(text),
      color: isCrit ? "#ff0055" : "#ffea00",
      life: 0.8,
      maxLife: 0.8,
      scale: 1.0,
    });
  }

  spawnParryRing(x, y) {
    this.addScreenShake(8.0);
    this.particles.push({
      x,
      y,
      vx: 0,
      vy: 0,
      size: 70,
      color: "#00ffff",
      life: 0.3,
      maxLife: 0.3,
      gravity: 0,
      shape: "ring",
      glow: true,
    });
  }
}
