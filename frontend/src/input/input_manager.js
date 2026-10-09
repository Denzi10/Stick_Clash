/**
 * Input Manager for Stick Clash.
 * Handles keyboard listeners and Gamepad API polling into server bitmasks.
 */

export const InputBits = {
  LEFT: 1 << 0,
  RIGHT: 1 << 1,
  UP: 1 << 2,
  DOWN: 1 << 3,
  LIGHT: 1 << 4,
  HEAVY: 1 << 5,
  SPECIAL: 1 << 6,
  DASH: 1 << 7,
  BLOCK: 1 << 8,
  GRAB: 1 << 9,
  RAGE: 1 << 10,
  EMOTE: 1 << 11,
};

export class InputManager {
  constructor() {
    this.keys = new Set();
    this.keymap = {
      KeyA: InputBits.LEFT,
      ArrowLeft: InputBits.LEFT,
      KeyD: InputBits.RIGHT,
      ArrowRight: InputBits.RIGHT,
      KeyW: InputBits.UP,
      ArrowUp: InputBits.UP,
      Space: InputBits.UP,
      KeyS: InputBits.DOWN,
      ArrowDown: InputBits.DOWN,
      KeyJ: InputBits.LIGHT,
      KeyK: InputBits.HEAVY,
      KeyL: InputBits.SPECIAL,
      KeyU: InputBits.DASH,
      ShiftLeft: InputBits.DASH,
      KeyI: InputBits.BLOCK,
      KeyO: InputBits.GRAB,
      KeyR: InputBits.RAGE,
      KeyE: InputBits.EMOTE,
    };

    window.addEventListener("keydown", (e) => {
      // Avoid scrolling on space/arrows
      if (["Space", "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(e.code)) {
        e.preventDefault();
      }
      this.keys.add(e.code);
    });

    window.addEventListener("keyup", (e) => {
      this.keys.delete(e.code);
    });
  }

  getBitmask() {
    let mask = 0;

    // Keyboard
    for (const code of this.keys) {
      if (this.keymap[code]) {
        mask |= this.keymap[code];
      }
    }

    // Gamepad API check
    const gamepads = navigator.getGamepads ? navigator.getGamepads() : [];
    if (gamepads && gamepads[0]) {
      const gp = gamepads[0];
      // Left stick
      if (gp.axes[0] < -0.3) mask |= InputBits.LEFT;
      if (gp.axes[0] > 0.3) mask |= InputBits.RIGHT;
      if (gp.axes[1] < -0.4) mask |= InputBits.UP;
      if (gp.axes[1] > 0.4) mask |= InputBits.DOWN;

      // Buttons
      if (gp.buttons[0]?.pressed) mask |= InputBits.UP; // A button: Jump
      if (gp.buttons[1]?.pressed) mask |= InputBits.GRAB; // B button: Grab
      if (gp.buttons[2]?.pressed) mask |= InputBits.LIGHT; // X button: Light
      if (gp.buttons[3]?.pressed) mask |= InputBits.HEAVY; // Y button: Heavy
      if (gp.buttons[4]?.pressed || gp.buttons[6]?.pressed) mask |= InputBits.BLOCK; // LB / LT: Block
      if (gp.buttons[5]?.pressed) mask |= InputBits.SPECIAL; // RB: Special
      if (gp.buttons[7]?.pressed) mask |= InputBits.DASH; // RT: Dash
      if (gp.buttons[9]?.pressed) mask |= InputBits.RAGE; // Start: Rage
    }

    return mask;
  }
}

export const inputManager = new InputManager();
