/**
 * Arena, Background Parallax, Platforms, and Hazards Renderer.
 */

export class ArenaView {
  constructor() {
    this.stars = Array.from({ length: 60 }, () => ({
      x: Math.random() * 1280,
      y: Math.random() * 400,
      r: Math.random() * 1.5 + 0.5,
      alpha: Math.random() * 0.7 + 0.3,
    }));
  }

  renderBackground(ctx, theme, now) {
    // 3 Parallax Layers: Sky gradient, Far decoration, Near grid
    if (theme === "snow") {
      const grad = ctx.createLinearGradient(0, 0, 0, 720);
      grad.addColorStop(0, "#081b29");
      grad.addColorStop(1, "#1e3a5f");
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 1280, 720);

      // Distant icy peaks
      ctx.fillStyle = "rgba(148, 197, 240, 0.15)";
      ctx.beginPath();
      ctx.moveTo(0, 720);
      ctx.lineTo(200, 320);
      ctx.lineTo(450, 720);
      ctx.lineTo(750, 260);
      ctx.lineTo(1100, 720);
      ctx.lineTo(1280, 480);
      ctx.lineTo(1280, 720);
      ctx.fill();
    } else if (theme === "volcano") {
      const grad = ctx.createLinearGradient(0, 0, 0, 720);
      grad.addColorStop(0, "#1f0907");
      grad.addColorStop(0.7, "#3b110a");
      grad.addColorStop(1, "#661807");
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 1280, 720);

      // Lava cavern stalactites
      ctx.fillStyle = "rgba(255, 70, 0, 0.12)";
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(300, 240);
      ctx.lineTo(600, 0);
      ctx.lineTo(950, 220);
      ctx.lineTo(1280, 0);
      ctx.fill();
    } else if (theme === "neon") {
      const grad = ctx.createLinearGradient(0, 0, 0, 720);
      grad.addColorStop(0, "#090d16");
      grad.addColorStop(1, "#130924");
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 1280, 720);

      // Distant cyberpunk skyscrapers
      ctx.fillStyle = "rgba(0, 240, 255, 0.08)";
      for (let i = 0; i < 10; i++) {
        ctx.fillRect(i * 130 + 20, 280 + (i % 3) * 60, 90, 440);
      }
    } else {
      // Default / Dojo / Temple
      const grad = ctx.createLinearGradient(0, 0, 0, 720);
      grad.addColorStop(0, "#0b0f19");
      grad.addColorStop(1, "#1a2234");
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 1280, 720);
    }

    // Celestial stars twinkle
    ctx.save();
    for (const star of this.stars) {
      ctx.fillStyle = `rgba(255, 255, 255, ${star.alpha * (0.7 + Math.sin(now * 3 + star.x) * 0.3)})`;
      ctx.beginPath();
      ctx.arc(star.x, star.y, star.r, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }

  renderPlatforms(ctx, platforms, now) {
    for (const p of platforms) {
      if (p.is_broken) continue;

      const left = p.x - p.width / 2;
      const top = p.y - p.height / 2;

      ctx.save();
      if (p.is_solid) {
        // Solid platform
        ctx.fillStyle = "#1e293b";
        ctx.fillRect(left, top, p.width, p.height);

        // Glowing trim
        ctx.strokeStyle = p.is_slippery ? "#38bdf8" : "#3b82f6";
        ctx.lineWidth = 2;
        ctx.strokeRect(left, top, p.width, p.height);

        // Top edge neon beam
        ctx.fillStyle = p.is_slippery ? "#7dd3fc" : "#60a5fa";
        ctx.fillRect(left, top, p.width, 3);
      } else {
        // One-way / Thin platform
        ctx.fillStyle = "rgba(30, 41, 59, 0.8)";
        ctx.fillRect(left, top, p.width, p.height);

        ctx.strokeStyle = p.is_crumbly ? "#f59e0b" : "#94a3b8";
        ctx.lineWidth = 2;
        ctx.setLineDash(p.is_crumbly ? [6, 4] : [12, 6]);
        ctx.strokeRect(left, top, p.width, p.height);

        // Rail glow
        ctx.fillStyle = p.is_crumbly ? "#fbbf24" : "#cbd5e1";
        ctx.fillRect(left, top, p.width, 2);
      }
      ctx.restore();
    }
  }

  renderHazards(ctx, hazards, now) {
    for (const h of hazards) {
      if (!h.active) continue;
      const left = h.x - h.width / 2;
      const top = h.y - h.height / 2;

      ctx.save();
      if (h.hazard_type.includes("lava")) {
        // Bubbling lava pool
        const grad = ctx.createLinearGradient(0, top, 0, top + h.height);
        grad.addColorStop(0, "#ff4500");
        grad.addColorStop(0.5, "#dc2626");
        grad.addColorStop(1, "#7f1d1d");
        ctx.fillStyle = grad;
        ctx.fillRect(left, top, h.width, h.height);

        // Lava glow
        ctx.shadowColor = "#ff4500";
        ctx.shadowBlur = 20;
        ctx.strokeStyle = "#fbbf24";
        ctx.lineWidth = 2;
        ctx.strokeRect(left, top, h.width, 2);
      } else if (h.hazard_type === "spikes") {
        ctx.fillStyle = "#ef4444";
        const numSpikes = Math.floor(h.width / 16);
        for (let i = 0; i < numSpikes; i++) {
          const sx = left + i * 16;
          ctx.beginPath();
          ctx.moveTo(sx, top + h.height);
          ctx.lineTo(sx + 8, top);
          ctx.lineTo(sx + 16, top + h.height);
          ctx.closePath();
          ctx.fill();
        }
      } else if (h.hazard_type === "bounce_pad") {
        ctx.fillStyle = "#06b6d4";
        ctx.fillRect(left, top, h.width, h.height);
        // Upward chevron arrows
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(h.x - 12, top + 14);
        ctx.lineTo(h.x, top + 4);
        ctx.lineTo(h.x + 12, top + 14);
        ctx.stroke();
      } else if (h.hazard_type === "conveyor") {
        ctx.fillStyle = "#334155";
        ctx.fillRect(left, top, h.width, h.height);
        // Striped hazard pattern
        ctx.strokeStyle = "#eab308";
        ctx.lineWidth = 4;
        const offset = (now * 60) % 20;
        for (let x = left - 20 + offset; x < left + h.width; x += 20) {
          ctx.beginPath();
          ctx.moveTo(x, top + h.height);
          ctx.lineTo(x + 10, top);
          ctx.stroke();
        }
      } else if (h.hazard_type === "crusher") {
        ctx.fillStyle = "#475569";
        ctx.fillRect(left, top, h.width, h.height);
        ctx.strokeStyle = "#f87171";
        ctx.lineWidth = 3;
        ctx.strokeRect(left, top, h.width, h.height);
      }
      ctx.restore();
    }
  }

  renderPickups(ctx, pickups, now) {
    for (const p of pickups) {
      ctx.save();
      ctx.translate(p.x, p.y);

      // Crate float bounce
      const bob = Math.sin(now * 6) * 3;
      ctx.translate(0, bob);

      // Rarity beacon
      const rarityColor = p.rarity === "epic" ? "#a855f7" : (p.rarity === "rare" ? "#3b82f6" : "#22c55e");
      ctx.shadowColor = rarityColor;
      ctx.shadowBlur = 14;

      // Crate box
      ctx.fillStyle = "#1e293b";
      ctx.fillRect(-14, -14, 28, 28);
      ctx.strokeStyle = rarityColor;
      ctx.lineWidth = 2;
      ctx.strokeRect(-14, -14, 28, 28);

      // Inner icon symbol
      ctx.fillStyle = rarityColor;
      ctx.font = "bold 12px 'Orbitron', sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(p.is_weapon ? "⚔" : "★", 0, 0);

      ctx.restore();
    }
  }

  renderProjectiles(ctx, projectiles) {
    for (const pr of projectiles) {
      ctx.save();
      ctx.translate(pr.x, pr.y);

      ctx.shadowBlur = 10;
      ctx.shadowColor = "#38bdf8";

      if (pr.item_type === "boomerang") {
        ctx.strokeStyle = "#ea580c";
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(0, 0, pr.radius, 0, Math.PI * 1.5);
        ctx.stroke();
      } else if (pr.item_type === "bomb") {
        ctx.fillStyle = "#0f172a";
        ctx.beginPath();
        ctx.arc(0, 0, pr.radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "#ef4444";
        ctx.fillRect(-2, -pr.radius - 4, 4, 4);
      } else {
        // Arrow or bullet
        ctx.fillStyle = "#38bdf8";
        ctx.beginPath();
        ctx.arc(0, 0, pr.radius, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();
    }
  }
}
