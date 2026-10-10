/**
 * Arena, Background Parallax, Platforms, and Hazards Renderer for Stick Clash.
 * Featuring Animated Deep Space Visuals, Cosmic Block & Altar Structures, and Void Survival Barrier.
 */

export class ArenaView {
  constructor() {
    // 140 Celestial stars with diverse colors, sizes, and twinkle cycles
    const starColors = ["#ffffff", "#67e8f9", "#c084fc", "#fef08a", "#f472b6", "#93c5fd"];
    this.stars = Array.from({ length: 140 }, () => ({
      x: Math.random() * 1280,
      y: Math.random() * 650,
      r: Math.random() * 1.8 + 0.4,
      alpha: Math.random() * 0.7 + 0.3,
      color: starColors[Math.floor(Math.random() * starColors.length)],
      twinkleSpeed: Math.random() * 2.5 + 1.2,
      twinkleOffset: Math.random() * Math.PI * 2,
    }));

    // Shooting stars / Cosmic meteors
    this.meteors = [
      { x: -100, y: 100, vx: 500, vy: 250, length: 140, active: false, timer: 1.0 },
      { x: -100, y: 220, vx: 620, vy: 310, length: 180, active: false, timer: 3.5 },
    ];

    // Floating asteroids / space rock debris
    this.asteroids = Array.from({ length: 6 }, (_, i) => ({
      x: (i * 220 + 80) % 1280,
      y: 90 + (i % 3) * 80,
      size: 16 + (i % 4) * 8,
      vx: (i % 2 === 0 ? 8 : -6),
      rot: Math.random() * Math.PI * 2,
      rotSpeed: (Math.random() - 0.5) * 0.4,
    }));
  }

  renderBackground(ctx, theme, now) {
    const isNeon = theme.includes("neon");
    const isVolcano = theme.includes("volcano");
    const isSnow = theme.includes("snow");
    const isSky = theme.includes("sky");
    const isJungle = theme.includes("jungle");

    // 1. Dynamic Space / Celestial Base Gradient
    const skyGrad = ctx.createRadialGradient(640, 280, 100, 640, 360, 800);
    if (isNeon) {
      skyGrad.addColorStop(0, "#19082e"); // Cyber violet
      skyGrad.addColorStop(0.4, "#090d1f");
      skyGrad.addColorStop(1, "#030408");
    } else if (isVolcano) {
      skyGrad.addColorStop(0, "#2c0905"); // Molten magma red
      skyGrad.addColorStop(0.4, "#140403");
      skyGrad.addColorStop(1, "#050101");
    } else if (isSnow) {
      skyGrad.addColorStop(0, "#051829"); // Arctic navy
      skyGrad.addColorStop(0.4, "#030d17");
      skyGrad.addColorStop(1, "#010408");
    } else if (isSky) {
      skyGrad.addColorStop(0, "#1d0c2e"); // Ether sunset
      skyGrad.addColorStop(0.4, "#0b1226");
      skyGrad.addColorStop(1, "#02040a");
    } else if (isJungle) {
      skyGrad.addColorStop(0, "#062118"); // Mystic emerald
      skyGrad.addColorStop(0.4, "#03120d");
      skyGrad.addColorStop(1, "#010504");
    } else {
      // Default: Deep Space Celestial Void
      skyGrad.addColorStop(0, "#0e0728"); // Nebula violet heart
      skyGrad.addColorStop(0.35, "#080c1d"); // Indigo space dust
      skyGrad.addColorStop(0.7, "#04060f"); // Deep celestial void
      skyGrad.addColorStop(1, "#020308"); // Event horizon black
    }
    ctx.fillStyle = skyGrad;
    ctx.fillRect(0, 0, 1280, 720);

    // 2. Swirling Cosmic Nebula Gas Clouds (Layered Organic Glows)
    ctx.save();
    ctx.globalCompositeOperation = "screen";

    const neb1Color = isVolcano
      ? "rgba(239, 68, 68, 0.18)"
      : isSnow
      ? "rgba(16, 185, 129, 0.16)"
      : isJungle
      ? "rgba(20, 184, 166, 0.16)"
      : "rgba(6, 182, 212, 0.16)";
    const neb2Color = isVolcano
      ? "rgba(245, 158, 11, 0.15)"
      : isNeon
      ? "rgba(244, 63, 94, 0.18)"
      : isSky
      ? "rgba(234, 179, 8, 0.15)"
      : "rgba(192, 38, 211, 0.15)";

    const neb1X = 350 + Math.sin(now * 0.15) * 40;
    const neb1Y = 220 + Math.cos(now * 0.12) * 30;
    const neb1 = ctx.createRadialGradient(neb1X, neb1Y, 30, neb1X, neb1Y, 380);
    neb1.addColorStop(0, neb1Color);
    neb1.addColorStop(0.5, "rgba(59, 130, 246, 0.06)");
    neb1.addColorStop(1, "rgba(0, 0, 0, 0)");
    ctx.fillStyle = neb1;
    ctx.fillRect(0, 0, 1280, 720);

    const neb2X = 920 + Math.cos(now * 0.18) * 50;
    const neb2Y = 260 + Math.sin(now * 0.14) * 35;
    const neb2 = ctx.createRadialGradient(neb2X, neb2Y, 40, neb2X, neb2Y, 420);
    neb2.addColorStop(0, neb2Color);
    neb2.addColorStop(0.5, "rgba(126, 34, 206, 0.05)");
    neb2.addColorStop(1, "rgba(0, 0, 0, 0)");
    ctx.fillStyle = neb2;
    ctx.fillRect(0, 0, 1280, 720);
    ctx.restore();

    // 3. Theme-Specific Background Scenery
    if (isNeon) {
      // Cyberpunk Skyscrapers in distance
      ctx.save();
      for (let i = 0; i < 9; i++) {
        const bX = i * 145 + 10;
        const bY = 320 + (i % 3) * 50;
        const bW = 90;
        const bH = 400;
        ctx.fillStyle = "rgba(15, 23, 42, 0.85)";
        ctx.fillRect(bX, bY, bW, bH);
        ctx.strokeStyle = "rgba(0, 240, 255, 0.2)";
        ctx.lineWidth = 1;
        ctx.strokeRect(bX, bY, bW, bH);

        // Neon windows
        ctx.fillStyle = (i % 2 === 0) ? "rgba(0, 240, 255, 0.35)" : "rgba(255, 0, 85, 0.3)";
        for (let wy = bY + 20; wy < 660; wy += 35) {
          ctx.fillRect(bX + 15, wy, 16, 12);
          ctx.fillRect(bX + 55, wy, 16, 12);
        }
      }
      ctx.restore();
    } else if (isSnow) {
      // Shimmering Aurora Borealis Curtains
      ctx.save();
      ctx.globalCompositeOperation = "screen";
      for (let j = 0; j < 3; j++) {
        ctx.strokeStyle = (j === 0) ? "rgba(52, 211, 153, 0.18)" : "rgba(56, 189, 248, 0.15)";
        ctx.lineWidth = 28;
        ctx.beginPath();
        for (let x = 0; x <= 1280; x += 40) {
          const ay = 140 + j * 40 + Math.sin(now * 1.2 + x * 0.005 + j) * 50;
          if (x === 0) ctx.moveTo(x, ay);
          else ctx.lineTo(x, ay);
        }
        ctx.stroke();
      }
      ctx.restore();
    } else if (isVolcano) {
      // Molten Magma Core Star & Rising Thermal Embers
      ctx.save();
      const sunGrad = ctx.createRadialGradient(640, 160, 20, 640, 160, 120);
      sunGrad.addColorStop(0, "rgba(255, 230, 150, 0.8)");
      sunGrad.addColorStop(0.4, "rgba(239, 68, 68, 0.45)");
      sunGrad.addColorStop(1, "rgba(220, 38, 38, 0)");
      ctx.fillStyle = sunGrad;
      ctx.beginPath();
      ctx.arc(640, 160, 120, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    } else {
      // Giant Celestial Ringed Planet & Orbiting Moon (Space Altar / Deep Space)
      ctx.save();
      const planetX = 1020;
      const planetY = 160;
      const planetR = 72;

      // Outer atmospheric glow
      const planetGlow = ctx.createRadialGradient(planetX, planetY, planetR * 0.8, planetX, planetY, planetR * 1.6);
      planetGlow.addColorStop(0, "rgba(56, 189, 248, 0.35)");
      planetGlow.addColorStop(0.6, "rgba(99, 102, 241, 0.12)");
      planetGlow.addColorStop(1, "rgba(0, 0, 0, 0)");
      ctx.fillStyle = planetGlow;
      ctx.beginPath();
      ctx.arc(planetX, planetY, planetR * 1.6, 0, Math.PI * 2);
      ctx.fill();

      // Planet Body Sphere
      const sphereGrad = ctx.createRadialGradient(planetX - 24, planetY - 24, 8, planetX, planetY, planetR);
      sphereGrad.addColorStop(0, "#bae6fd");
      sphereGrad.addColorStop(0.3, "#38bdf8");
      sphereGrad.addColorStop(0.7, "#1e3a8a");
      sphereGrad.addColorStop(1, "#090d16");
      ctx.fillStyle = sphereGrad;
      ctx.beginPath();
      ctx.arc(planetX, planetY, planetR, 0, Math.PI * 2);
      ctx.fill();

      // Planet Atmospheric Bands
      ctx.save();
      ctx.clip();
      ctx.strokeStyle = "rgba(14, 165, 233, 0.25)";
      ctx.lineWidth = 14;
      ctx.beginPath();
      ctx.arc(planetX, planetY - 15, planetR + 10, 0, Math.PI * 2);
      ctx.stroke();
      ctx.strokeStyle = "rgba(192, 132, 252, 0.2)";
      ctx.lineWidth = 10;
      ctx.beginPath();
      ctx.arc(planetX, planetY + 18, planetR + 10, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();

      // Planetary Rings
      ctx.save();
      ctx.translate(planetX, planetY);
      ctx.rotate(-0.4);
      ctx.strokeStyle = "rgba(224, 242, 254, 0.45)";
      ctx.lineWidth = 5;
      ctx.beginPath();
      ctx.ellipse(0, 0, planetR * 1.85, planetR * 0.36, 0, 0, Math.PI * 2);
      ctx.stroke();
      ctx.strokeStyle = "rgba(56, 189, 248, 0.25)";
      ctx.lineWidth = 12;
      ctx.beginPath();
      ctx.ellipse(0, 0, planetR * 2.1, planetR * 0.42, 0, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();

      // Orbiting Satellite Moon
      const moonAngle = now * 0.4;
      const moonDistX = Math.cos(moonAngle) * 150;
      const moonDistY = Math.sin(moonAngle) * 45;
      ctx.fillStyle = "#e2e8f0";
      ctx.shadowColor = "#94a3b8";
      ctx.shadowBlur = 8;
      ctx.beginPath();
      ctx.arc(planetX + moonDistX, planetY + moonDistY, 10, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }

    // 4. Parallax Twinkling Stars
    ctx.save();
    for (const star of this.stars) {
      const alphaPulse = star.alpha * (0.65 + Math.sin(now * star.twinkleSpeed + star.twinkleOffset) * 0.35);
      ctx.fillStyle = star.color;
      ctx.globalAlpha = Math.max(0.15, Math.min(1.0, alphaPulse));
      ctx.beginPath();
      ctx.arc(star.x, star.y, star.r, 0, Math.PI * 2);
      ctx.fill();

      // Rare star sparkle cross
      if (star.r > 1.8 && alphaPulse > 0.8) {
        ctx.strokeStyle = star.color;
        ctx.lineWidth = 0.8;
        ctx.beginPath();
        ctx.moveTo(star.x - star.r * 2.2, star.y);
        ctx.lineTo(star.x + star.r * 2.2, star.y);
        ctx.moveTo(star.x, star.y - star.r * 2.2);
        ctx.lineTo(star.x, star.y + star.r * 2.2);
        ctx.stroke();
      }
    }
    ctx.restore();

    // 5. Shooting Stars / Cosmic Meteors
    for (const m of this.meteors) {
      m.timer -= 0.016;
      if (m.timer <= 0 && !m.active) {
        m.active = true;
        m.x = Math.random() * 800;
        m.y = Math.random() * 200;
      }
      if (m.active) {
        m.x += m.vx * 0.016;
        m.y += m.vy * 0.016;

        ctx.save();
        const trailGrad = ctx.createLinearGradient(
          m.x,
          m.y,
          m.x - (m.vx * 0.16),
          m.y - (m.vy * 0.16)
        );
        trailGrad.addColorStop(0, "rgba(255, 255, 255, 0.9)");
        trailGrad.addColorStop(0.2, "rgba(56, 189, 248, 0.7)");
        trailGrad.addColorStop(1, "rgba(147, 51, 234, 0)");

        ctx.strokeStyle = trailGrad;
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        ctx.moveTo(m.x, m.y);
        ctx.lineTo(m.x - (m.vx * 0.16), m.y - (m.vy * 0.16));
        ctx.stroke();

        // Meteor Head Spark
        ctx.fillStyle = "#ffffff";
        ctx.shadowColor = "#38bdf8";
        ctx.shadowBlur = 10;
        ctx.beginPath();
        ctx.arc(m.x, m.y, 2.5, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();

        if (m.x > 1400 || m.y > 600) {
          m.active = false;
          m.timer = Math.random() * 4.0 + 2.5;
        }
      }
    }

    // 6. Floating Asteroid Debris
    ctx.save();
    for (const ast of this.asteroids) {
      ast.x += ast.vx * 0.016;
      ast.rot += ast.rotSpeed * 0.016;
      if (ast.x < -60) ast.x = 1340;
      if (ast.x > 1340) ast.x = -60;

      ctx.save();
      ctx.translate(ast.x, ast.y);
      ctx.rotate(ast.rot);

      ctx.fillStyle = "#1e293b";
      ctx.strokeStyle = "rgba(148, 163, 184, 0.4)";
      ctx.lineWidth = 1.5;

      const s = ast.size;
      ctx.beginPath();
      ctx.moveTo(-s * 0.5, -s * 0.8);
      ctx.lineTo(s * 0.6, -s * 0.7);
      ctx.lineTo(s * 0.9, s * 0.2);
      ctx.lineTo(s * 0.3, s * 0.8);
      ctx.lineTo(-s * 0.6, s * 0.7);
      ctx.lineTo(-s * 0.9, -s * 0.1);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      ctx.restore();
    }
    ctx.restore();
  }

  /**
   * Render Block Structures & Altar Platforms with 3D Depth, Neon Edge Trims & Runes
   */
  renderPlatforms(ctx, platforms, now) {
    if (!platforms || platforms.length === 0) return;

    for (const p of platforms) {
      const left = p.x - p.width / 2;
      const top = p.y - p.height / 2;
      const w = p.width;
      const h = p.height;

      ctx.save();

      if (p.is_solid) {
        // === SOLID BLOCK / ALTAR PLATFORM STRUCTURE ===
        const isAltar = p.id.includes("altar");
        const themeColor = isAltar ? "#ffb700" : "#00f0ff";
        const themeSecondary = isAltar ? "#f59e0b" : "#3b82f6";

        // 1. Drop shadow glow
        ctx.shadowColor = themeColor;
        ctx.shadowBlur = isAltar ? 16 : 10;

        // 2. 3D Extrusion Depth (Bottom & Sides bevel)
        const bevelDepth = 8;
        ctx.fillStyle = "#090d16";
        ctx.fillRect(left, top + bevelDepth, w, h);

        // 3. Main Block Face
        const blockGrad = ctx.createLinearGradient(left, top, left, top + h);
        blockGrad.addColorStop(0, "#1a2436");
        blockGrad.addColorStop(0.5, "#0f172a");
        blockGrad.addColorStop(1, "#090d16");
        ctx.fillStyle = blockGrad;
        ctx.fillRect(left, top, w, h);

        // 4. Perimeter Neon Cyber Frame
        ctx.strokeStyle = themeColor;
        ctx.lineWidth = isAltar ? 2.5 : 2;
        ctx.strokeRect(left, top, w, h);

        // 5. Top Stand Surface Runway (Where stickman stands)
        const topStrip = ctx.createLinearGradient(left, top, left + w, top);
        topStrip.addColorStop(0, "rgba(255, 255, 255, 0.4)");
        topStrip.addColorStop(0.5, themeColor);
        topStrip.addColorStop(1, "rgba(255, 255, 255, 0.4)");
        ctx.fillStyle = topStrip;
        ctx.fillRect(left, top, w, 4);

        // 6. Altar Sacred Runes & Cyber Plate Lines
        ctx.strokeStyle = `rgba(${isAltar ? "255, 183, 0" : "0, 240, 255"}, 0.35)`;
        ctx.lineWidth = 1.2;

        // Tech Panels / Divisions
        const divisions = Math.max(2, Math.floor(w / 80));
        for (let d = 1; d < divisions; d++) {
          const divX = left + (w / divisions) * d;
          ctx.beginPath();
          ctx.moveTo(divX, top + 5);
          ctx.lineTo(divX, top + h - 5);
          ctx.stroke();

          // Corner bolt rivets
          ctx.fillStyle = themeColor;
          ctx.fillRect(divX - 1.5, top + 6, 3, 3);
          ctx.fillRect(divX - 1.5, top + h - 9, 3, 3);
        }

        // Center Altar Power Glyph / Rune
        if (isAltar) {
          const centerX = p.x;
          const centerY = p.y + 2;
          ctx.save();
          ctx.strokeStyle = "#ffea00";
          ctx.lineWidth = 1.8;
          ctx.shadowColor = "#ffea00";
          ctx.shadowBlur = 12;

          // Diamond rune
          ctx.beginPath();
          ctx.moveTo(centerX, centerY - 8);
          ctx.lineTo(centerX + 12, centerY);
          ctx.lineTo(centerX, centerY + 8);
          ctx.lineTo(centerX - 12, centerY);
          ctx.closePath();
          ctx.stroke();

          // Inner glowing core
          ctx.fillStyle = `rgba(255, 234, 0, ${0.5 + Math.sin(now * 5) * 0.4})`;
          ctx.beginPath();
          ctx.arc(centerX, centerY, 4, 0, Math.PI * 2);
          ctx.fill();
          ctx.restore();
        }

        // Corner Defense Brackets
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2;
        // Top-Left
        ctx.strokeRect(left, top, 6, 6);
        // Top-Right
        ctx.strokeRect(left + w - 6, top, 6, 6);
      } else {
        // === ONE-WAY / HIGH CELESTIAL TIER (Holographic Energy Platform) ===
        const isCrumbly = p.is_crumbly;
        const tierColor = isCrumbly ? "#f59e0b" : "#a855f7";

        ctx.shadowColor = tierColor;
        ctx.shadowBlur = 8;

        // Semi-transparent cosmic glass slab
        ctx.fillStyle = "rgba(15, 23, 42, 0.72)";
        ctx.fillRect(left, top, w, h);

        // Dashed glowing energy rails
        ctx.strokeStyle = tierColor;
        ctx.lineWidth = 2;
        ctx.setLineDash(isCrumbly ? [6, 4] : [12, 6]);
        ctx.strokeRect(left, top, w, h);
        ctx.setLineDash([]);

        // Top laser surface
        ctx.fillStyle = isCrumbly ? "#fbbf24" : "#c084fc";
        ctx.fillRect(left, top, w, 2.5);

        // Pulse energy nodes on ends
        const nodeGlow = 0.5 + Math.sin(now * 4 + p.x) * 0.4;
        ctx.fillStyle = `rgba(192, 132, 252, ${nodeGlow})`;
        ctx.fillRect(left, top, 6, h);
        ctx.fillRect(left + w - 6, top, 6, h);
      }

      ctx.restore();
    }
  }

  /**
   * Render the Danger Void Barrier / Survival Line
   * Character must remain on the blocks above this line to survive!
   */
  renderSurvivalLine(ctx, now) {
    const y = 665;
    ctx.save();

    // 1. Pulsing Energy Hazard Beam
    const pulse = Math.sin(now * 6) * 0.25 + 0.75;
    const grad = ctx.createLinearGradient(0, y - 6, 0, y + 14);
    grad.addColorStop(0, "rgba(255, 0, 85, 0)");
    grad.addColorStop(0.3, `rgba(255, 0, 85, ${0.4 * pulse})`);
    grad.addColorStop(0.5, `rgba(255, 50, 100, ${0.9 * pulse})`);
    grad.addColorStop(0.7, `rgba(255, 0, 85, ${0.5 * pulse})`);
    grad.addColorStop(1, "rgba(255, 0, 85, 0)");

    ctx.fillStyle = grad;
    ctx.fillRect(0, y - 6, 1280, 20);

    // 2. High-intensity Central Laser Line
    ctx.strokeStyle = `rgba(255, 255, 255, ${pulse})`;
    ctx.lineWidth = 2;
    ctx.shadowColor = "#ff0055";
    ctx.shadowBlur = 14;
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(1280, y);
    ctx.stroke();

    // 3. Hazard Striped Warning Chevrons along survival boundary
    ctx.save();
    ctx.strokeStyle = `rgba(255, 183, 0, ${0.35 * pulse})`;
    ctx.lineWidth = 3;
    const offset = (now * 50) % 30;
    for (let x = -30 + offset; x < 1280; x += 30) {
      ctx.beginPath();
      ctx.moveTo(x, y + 10);
      ctx.lineTo(x + 10, y + 1);
      ctx.stroke();
    }
    ctx.restore();

    // 4. Survival Line Warning Hologram Label
    ctx.fillStyle = `rgba(255, 80, 120, ${0.85 * pulse})`;
    ctx.font = "bold 10px 'Orbitron', sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("▲ ⚠️ VOID HAZARD BOUNDARY — SURVIVE ABOVE THIS LINE ⚠️ ▲", 640, y + 16);

    ctx.restore();
  }

  renderHazards(ctx, hazards, now) {
    if (!hazards) return;
    for (const h of hazards) {
      if (!h.active) continue;
      const left = h.x - h.width / 2;
      const top = h.y - h.height / 2;

      ctx.save();
      if (h.hazard_type === "void_barrier") {
        // Void barrier handled by renderSurvivalLine
        continue;
      } else if (h.hazard_type.includes("lava")) {
        const grad = ctx.createLinearGradient(0, top, 0, top + h.height);
        grad.addColorStop(0, "#ff4500");
        grad.addColorStop(0.5, "#dc2626");
        grad.addColorStop(1, "#7f1d1d");
        ctx.fillStyle = grad;
        ctx.fillRect(left, top, h.width, h.height);
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
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(h.x - 12, top + 14);
        ctx.lineTo(h.x, top + 4);
        ctx.lineTo(h.x + 12, top + 14);
        ctx.stroke();
      }
      ctx.restore();
    }
  }

  renderPickups(ctx, pickups, now) {
    if (!pickups) return;
    for (const p of pickups) {
      ctx.save();
      ctx.translate(p.x, p.y);

      const bob = Math.sin(now * 6) * 3;
      ctx.translate(0, bob);

      const rarityColor = p.rarity === "epic" ? "#a855f7" : (p.rarity === "rare" ? "#3b82f6" : "#22c55e");
      ctx.shadowColor = rarityColor;
      ctx.shadowBlur = 14;

      ctx.fillStyle = "#1e293b";
      ctx.fillRect(-14, -14, 28, 28);
      ctx.strokeStyle = rarityColor;
      ctx.lineWidth = 2;
      ctx.strokeRect(-14, -14, 28, 28);

      ctx.fillStyle = rarityColor;
      ctx.font = "bold 12px 'Orbitron', sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(p.is_weapon ? "⚔" : "★", 0, 0);

      ctx.restore();
    }
  }

  renderProjectiles(ctx, projectiles) {
    if (!projectiles) return;
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
        ctx.fillStyle = "#38bdf8";
        ctx.beginPath();
        ctx.arc(0, 0, pr.radius, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();
    }
  }
}
