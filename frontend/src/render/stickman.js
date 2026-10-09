/**
 * Procedural Articulated Stickman Renderer for Stick Clash.
 * Renders joints, limbs, weapons, class details, and KO ragdolls.
 */

export class StickmanRenderer {
  constructor() {
    this.ragdolls = new Map(); // player_id -> ragdoll segments
  }

  render(ctx, player, now) {
    const { x, y, facing, team, fighter_class, action_state, action_frame, is_ragdoll, is_in_rage } = player;

    // Team colors
    const primaryColor = team === 0 ? "#00f0ff" : "#ff0055";
    const glowColor = team === 0 ? "rgba(0, 240, 255, 0.6)" : "rgba(255, 0, 85, 0.6)";

    if (is_ragdoll) {
      this.renderRagdoll(ctx, player, primaryColor);
      return;
    }

    ctx.save();
    ctx.translate(x, y);

    // Invulnerability blinking
    if (player.is_invulnerable && Math.floor(now * 15) % 2 === 0) {
      ctx.globalAlpha = 0.35;
    }

    // Rage Mode Aura
    if (player.is_in_rage) {
      this.renderRageAura(ctx, now);
    }

    // Shield Bubble effect
    const hasShield = player.statuses && player.statuses.some((s) => s.status_type === "shield");
    if (hasShield) {
      ctx.save();
      ctx.strokeStyle = "rgba(0, 255, 200, 0.8)";
      ctx.lineWidth = 3;
      ctx.shadowColor = "#00ffc8";
      ctx.shadowBlur = 15;
      ctx.beginPath();
      ctx.arc(0, -45, 42, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    }

    // Freeze ice block effect
    const isFrozen = player.statuses && player.statuses.some((s) => s.status_type === "freeze");
    if (isFrozen) {
      ctx.save();
      ctx.fillStyle = "rgba(100, 220, 255, 0.45)";
      ctx.strokeStyle = "rgba(180, 245, 255, 0.9)";
      ctx.lineWidth = 3;
      ctx.strokeRect(-25, -92, 50, 92);
      ctx.fillRect(-25, -92, 50, 92);
      ctx.restore();
    }

    // Directional flip
    ctx.scale(facing, 1);

    // Kinematic poses based on state
    ctx.strokeStyle = primaryColor;
    ctx.fillStyle = primaryColor;
    ctx.lineWidth = 4;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.shadowColor = glowColor;
    ctx.shadowBlur = 10;

    const animTime = now * 10;
    let headY = -76;
    let chestY = -60;
    let hipY = -38;

    let lLegAngle = 0.2;
    let rLegAngle = -0.2;
    let lArmAngle = -0.3;
    let rArmAngle = 0.3;

    if (action_state === "run") {
      lLegAngle = Math.sin(animTime) * 0.75;
      rLegAngle = -Math.sin(animTime) * 0.75;
      lArmAngle = -Math.sin(animTime) * 0.8;
      rArmAngle = Math.sin(animTime) * 0.8;
      headY += Math.abs(Math.sin(animTime)) * 3;
    } else if (action_state === "jump" || !player.is_grounded) {
      lLegAngle = 0.5;
      rLegAngle = -0.4;
      lArmAngle = -1.2;
      rArmAngle = -0.9;
    } else if (action_state === "dash") {
      chestY = -52;
      hipY = -34;
      lLegAngle = -1.1;
      rLegAngle = -0.8;
      lArmAngle = 1.3;
      rArmAngle = 1.1;
    } else if (action_state === "light1" || action_state === "light2" || action_state === "light3") {
      rArmAngle = 1.2 + Math.min(1.0, action_frame * 0.2);
      lArmAngle = -0.5;
      rLegAngle = 0.6;
    } else if (action_state === "heavy") {
      rArmAngle = action_frame < 14 ? -1.4 : 1.4;
      lArmAngle = -0.6;
    } else if (action_state === "slam") {
      lArmAngle = 2.0;
      rArmAngle = 2.0;
      lLegAngle = -0.6;
      rLegAngle = -0.6;
    } else if (player.is_blocking) {
      rArmAngle = 1.0;
      lArmAngle = 0.9;
      // Draw energetic guard shield
      ctx.save();
      ctx.strokeStyle = "rgba(255, 230, 0, 0.8)";
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.arc(24, -48, 28, -Math.PI * 0.4, Math.PI * 0.4);
      ctx.stroke();
      ctx.restore();
    }

    // 1. Head
    ctx.beginPath();
    ctx.arc(0, headY, 11, 0, Math.PI * 2);
    ctx.stroke();

    // Class Accessory
    this.renderClassAccessory(ctx, fighter_class, headY);

    // 2. Spine / Torso
    ctx.beginPath();
    ctx.moveTo(0, chestY);
    ctx.lineTo(0, hipY);
    ctx.stroke();

    // 3. Left Leg (back)
    const kneeLX = Math.sin(lLegAngle) * 20;
    const kneeLY = hipY + Math.cos(lLegAngle) * 20;
    const footLX = kneeLX + Math.sin(lLegAngle * 0.6) * 18;
    const footLY = kneeLY + Math.cos(lLegAngle * 0.6) * 18;
    ctx.beginPath();
    ctx.moveTo(0, hipY);
    ctx.lineTo(kneeLX, kneeLY);
    ctx.lineTo(footLX, footLY);
    ctx.stroke();

    // 4. Right Leg (front)
    const kneeRX = Math.sin(rLegAngle) * 20;
    const kneeRY = hipY + Math.cos(rLegAngle) * 20;
    const footRX = kneeRX + Math.sin(rLegAngle * 0.6) * 18;
    const footRY = kneeRY + Math.cos(rLegAngle * 0.6) * 18;
    ctx.beginPath();
    ctx.moveTo(0, hipY);
    ctx.lineTo(kneeRX, kneeRY);
    ctx.lineTo(footRX, footRY);
    ctx.stroke();

    // 5. Left Arm (back)
    const elbowLX = Math.sin(lArmAngle) * 16;
    const elbowLY = chestY + Math.cos(lArmAngle) * 16;
    const handLX = elbowLX + Math.sin(lArmAngle) * 15;
    const handLY = elbowLY + Math.cos(lArmAngle) * 15;
    ctx.beginPath();
    ctx.moveTo(0, chestY);
    ctx.lineTo(elbowLX, elbowLY);
    ctx.lineTo(handLX, handLY);
    ctx.stroke();

    // 6. Right Arm (front - holds weapon)
    const elbowRX = Math.sin(rArmAngle) * 18;
    const elbowRY = chestY + Math.cos(rArmAngle) * 18;
    const handRX = elbowRX + Math.sin(rArmAngle) * 16;
    const handRY = elbowRY + Math.cos(rArmAngle) * 16;
    ctx.beginPath();
    ctx.moveTo(0, chestY);
    ctx.lineTo(elbowRX, elbowRY);
    ctx.lineTo(handRX, handRY);
    ctx.stroke();

    // 7. Weapon rendering attached to front hand
    if (player.held_weapon) {
      this.renderWeapon(ctx, player.held_weapon.weapon_type, handRX, handRY, rArmAngle);
    }

    ctx.restore();
  }

  renderClassAccessory(ctx, fClass, headY) {
    if (fClass === "ninja") {
      // Flowing red headband tails
      ctx.save();
      ctx.strokeStyle = "#ff0033";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(-9, headY - 2);
      ctx.quadraticCurveTo(-22, headY - 6, -30, headY - 14);
      ctx.stroke();
      ctx.restore();
    } else if (fClass === "mage") {
      // Wizard hat tip & arcane glow
      ctx.save();
      ctx.fillStyle = "#a855f7";
      ctx.beginPath();
      ctx.moveTo(-12, headY - 6);
      ctx.lineTo(12, headY - 6);
      ctx.lineTo(0, headY - 24);
      ctx.closePath();
      ctx.fill();
      ctx.restore();
    } else if (fClass === "bruiser") {
      // Heavy shoulder pauldron horns
      ctx.save();
      ctx.strokeStyle = "#ffaa00";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(-10, headY + 12);
      ctx.lineTo(-18, headY + 4);
      ctx.moveTo(10, headY + 12);
      ctx.lineTo(18, headY + 4);
      ctx.stroke();
      ctx.restore();
    }
  }

  renderWeapon(ctx, weaponType, hx, hy, armAngle) {
    ctx.save();
    ctx.translate(hx, hy);
    ctx.rotate(armAngle);

    if (weaponType === "sword") {
      ctx.strokeStyle = "#e2e8f0";
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(35, -20);
      ctx.stroke();
      // Guard
      ctx.strokeStyle = "#ffd700";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(4, -8);
      ctx.lineTo(-4, 4);
      ctx.stroke();
    } else if (weaponType === "bat") {
      ctx.strokeStyle = "#d97706";
      ctx.lineWidth = 6;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(30, -18);
      ctx.stroke();
    } else if (weaponType === "hammer") {
      ctx.strokeStyle = "#64748b";
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(28, -20);
      ctx.stroke();
      // Hammer head
      ctx.fillStyle = "#334155";
      ctx.fillRect(20, -32, 20, 16);
    } else if (weaponType === "spear") {
      ctx.strokeStyle = "#94a3b8";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(-10, 10);
      ctx.lineTo(55, -35);
      ctx.stroke();
    } else if (weaponType === "bow") {
      ctx.strokeStyle = "#a16207";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(15, -10, 20, -Math.PI * 0.4, Math.PI * 0.4);
      ctx.stroke();
    } else if (weaponType === "pistol") {
      ctx.fillStyle = "#1e293b";
      ctx.fillRect(0, -6, 18, 7);
      ctx.fillRect(2, -2, 5, 8);
    } else if (weaponType === "boomerang") {
      ctx.strokeStyle = "#ea580c";
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.moveTo(0, -14);
      ctx.lineTo(12, 0);
      ctx.lineTo(0, 14);
      ctx.stroke();
    }

    ctx.restore();
  }

  renderRageAura(ctx, now) {
    ctx.save();
    ctx.shadowBlur = 24;
    ctx.shadowColor = "#ff5500";
    ctx.fillStyle = "rgba(255, 85, 0, 0.25)";
    ctx.beginPath();
    ctx.arc(0, -45, 48 + Math.sin(now * 20) * 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  renderRagdoll(ctx, player, color) {
    ctx.save();
    ctx.translate(player.x, player.y);
    ctx.strokeStyle = "#64748b";
    ctx.lineWidth = 4;
    // Collapsed lines on floor
    ctx.beginPath();
    ctx.arc(0, -10, 9, 0, Math.PI * 2);
    ctx.moveTo(0, -5);
    ctx.lineTo(20, -2);
    ctx.lineTo(35, 0);
    ctx.moveTo(0, -5);
    ctx.lineTo(-18, -2);
    ctx.lineTo(-30, 0);
    ctx.stroke();
    ctx.restore();
  }
}
