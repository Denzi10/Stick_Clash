<div align="center">

# ⚔️ STICK CLASH

### Fast-Paced 2D Online Stickman Platform Brawler

[![Python 3.13](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![WebSockets](https://img.shields.io/badge/WebSockets-60Hz_Sync-blueviolet?style=for-the-badge&logo=websocket&logoColor=white)](https://websockets.readthedocs.io/)
[![Vite](https://img.shields.io/badge/Vite-5.4+-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![HTML5 Canvas](https://img.shields.io/badge/Rendering-HTML5_Canvas-E34F26?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API)
[![Cloudflare Tunnel](https://img.shields.io/badge/Cloudflare-Quick_Tunnel-F38020?style=for-the-badge&logo=cloudflare&logoColor=white)](https://cloudflare.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE.md)

<p align="center">
  <b>Instant matchmaking • Shareable 5-character room links • 4 Fighter classes • 8 Arenas with dynamic hazards • Gauntlet continuous mode • 20 Automated test suites</b>
</p>

</div>

---

## 🌟 Product Highlights

- **Instant Multiplayer**: Spin up a match and share an instant link (`/?room=ABCDE`) or 5-character room code.
- **Microservices Architecture**: Cleanly decoupled Python FastAPI backend and modern Vite frontend.
- **Deterministic 60 Hz Simulation**: Authoritative server loop with AABB physics, client prediction, and 20 Hz delta-compressed snapshot broadcasts.
- **Deep Combat Systems**: Light 3-hit combos, hold-to-charge heavy strikes, down-air slams, parrying with an 8-frame counter window, guard breaks, and Rage Mode.
- **Dynamic Content**: 4 Fighter classes, 8 weapons with durability, 12 throwables and power-ups, 8 elemental status effects, and 8 hazard-filled arenas.
- **Gauntlet Mode**: Continuous roguelike progression with 3-card upgrade drafting between levels and epic Stone Golem boss encounters.
- **Cloudflare Quick Tunnel**: One-click public HTTPS/WSS URL generation for instant remote playtesting with friends over the internet without port forwarding.

---

## 🏛️ Microservices Architecture

```
Stick_Clash/
├── backend/                  # Authoritative Game Server
│   ├── app/
│   │   ├── main.py           # FastAPI app, REST API, WebSocket router
│   │   ├── config.py         # 60Hz tick rates, physics constants, canvas limits
│   │   ├── models/           # Pydantic state schemas, snapshots, events
│   │   ├── simulation/       # Physics, combat, classes, weapons, statuses, arenas
│   │   ├── modes/            # Duel (1v1), Team Clash (2v2), FFA, Gauntlet
│   │   ├── bot/              # FSM AI with Easy/Normal/Hard behaviors & slot fill
│   │   └── rooms/            # Room manager, 5-char code generator, matchmaking
│   ├── tests/                # 20 Automated Pytest unit test suites
│   ├── requirements.txt      # FastAPI, Uvicorn, WebSockets, Pytest
│   └── pytest.ini            # Test environment configuration
│
├── frontend/                 # Client Microservice
│   ├── src/
│   │   ├── main.js           # Game coordinator & screen manager
│   │   ├── render/           # Articulated stickman, parallax backgrounds, particles
│   │   ├── net/              # WebSocket client, input streaming, snapshot dispatch
│   │   ├── audio/            # Web Audio API procedural SFX & chiptune synth
│   │   ├── ui/               # Glassmorphism HUD, lobby view, 3-card upgrades
│   │   └── input/            # Keyboard & Gamepad API polling
│   ├── styles/               # Cyber-arcade CSS theme with glassmorphism
│   ├── index.html            # Main entry point & canvas surface
│   └── vite.config.js        # Vite dev server with backend API/WS proxy
│
├── tools/                    # Tooling & Orchestration
│   ├── dev.py                # Launches backend, frontend & tunnel concurrently
│   └── run_tunnel.py         # Cloudflare Quick Tunnel runner (outputs public URL)
│
├── docs/                     # Full project specification documents
├── LICENSE.md                # MIT License
└── README.md                 # Project documentation
```

---

## 🎮 Fighter Classes

| Class | Health | Speed | Damage | Weight | Passive Trait | Special Ability (Costs 50 Power) |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **Brawler** | 100 | 300 px/s | 1.0x | 1.0 | +10 Max Guard | **Quake Slam**: Leap and slam creating an 180px shockwave with 0.8s knockdown. |
| **Ninja** | 85 | 345 px/s | 0.9x | 0.85 | Extra Air Dash per jump | **Shadow Dash**: Phase 320px through enemies dealing piercing strike damage. |
| **Mage** | 80 | 285 px/s | 0.95x | 0.9 | Arcane Bolt light attacks | **Elemental Blast**: Long-range bolt (600px) applying alternating Freeze and Burn. |
| **Bruiser** | 130 | 255 px/s | 1.2x | 1.3 | Super Armor during heavies | **Charge Tackle**: Bull-rush 260px carrying enemies with a 0.5s stun. |

---

## 🗺️ Arenas & Interactive Hazards

| Arena | Theme | Features & Hazards | Best For |
| :--- | :--- | :--- | :--- |
| **Snow Peaks** | Icy Mountains | Slippery ice floors (friction 0.3), danger spike pits | All Modes |
| **Volcano Pit** | Lava Cavern | Rising lava pool that surges 40px every 20 seconds | FFA & Gauntlet |
| **Neon City** | Cyber Rooftops | Moving platforms on fixed paths and bounce pads | Team Clash |
| **Jungle Ruins** | Overgrown Temple | Bounce mushrooms launching fighters at 1000 px/s | FFA |
| **Sky Islands** | Floating Citadels | Horizontal wind gusts (150 px/s) and crumbling platforms | Team Clash |
| **Factory Floor** | Industrial Complex | High-speed conveyor belts (120 px/s) and hydraulic crushers | Gauntlet |
| **Crystal Cave** | Subterranean Geode | Falling crystal stalactites telegraphed by shadows | FFA |
| **Training Dojo** | Traditional Dojo | Clean symmetric layout with no hazards | Duel 1v1 |

---

## 🕹️ Controls Guide

| Action | Keyboard | Gamepad (Xbox / PlayStation) |
| :--- | :--- | :--- |
| **Move Left / Right** | `A` / `D` or `←` / `→` | Left Analog Stick / D-Pad |
| **Jump / Double Jump** | `W`, `Space`, or `↑` | `A` Button (Cross) |
| **Drop Through / Fast Fall** | `S` or `↓` | Down on Stick |
| **Light Attack (Combo)** | `J` | `X` Button (Square) |
| **Heavy Attack (Chargeable)** | `K` (hold to charge +50%) | `Y` Button (Triangle) |
| **Dash (Invulnerable)** | `U` or `Shift` | `RT` Trigger / `R2` |
| **Block / Parry** | `I` (tap within 8f to parry) | `LT` Trigger / `L2` |
| **Grab / Throw / Pickup** | `O` | `B` Button (Circle) |
| **Special Move** | `L` (costs 50 power) | `RB` Bumper / `R1` |
| **Rage Mode** | `R` (costs 100 power) | Start Button / `Y+B` |
| **Quick Emotes** | `E` | D-Pad |

---

## 🚀 Running the Game (Terminal Commands)

Whenever you want to run the project, open PowerShell and use these commands:

### ⚡ Method 1: All-In-One Command (Fastest)
Runs the **Backend**, **Frontend**, and **Cloudflare Online Tunnel** concurrently in a single terminal:

```powershell
& "F:\project D\backend\venv\Scripts\python.exe" "F:\project D\tools\dev.py"
```

---

### 💻 Method 2: Running Microservices in Separate Terminals (Standard)

Open two PowerShell windows:

#### 🔹 Terminal 1 — Backend Game Server (FastAPI on Port 8000)
```powershell
cd "F:\project D\backend"
& ".\venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Local API Docs:* [http://localhost:8000/docs](http://localhost:8000/docs)

#### 🔹 Terminal 2 — Frontend Game Client (Vite on Port 5173)
```powershell
$env:Path += ";C:\Users\denzs\.gemini\antigravity-ide\bin"
cd "F:\project D\frontend"
npm run dev
```
*Local Game Surface:* [http://localhost:5173](http://localhost:5173)

---

### 🌐 Method 3: Cloudflare Online Link (Play with Friends Over Internet)

To generate a shareable public HTTPS link for friends without port forwarding, open a 3rd PowerShell window:

```powershell
cd "F:\project D"
& ".\backend\venv\Scripts\python.exe" tools/run_tunnel.py http://127.0.0.1:5173
```
*Copy the generated `https://xxxx.trycloudflare.com` link and share it with other players!*

---

### 🧪 Automated Testing Command
Run all 20 physics, combat, bot AI, and gauntlet test suites:

```powershell
cd "F:\project D\backend"
& ".\venv\Scripts\pytest.exe" -v
```

---

### 📦 Git Push Command (Sync to GitHub)
```powershell
& "C:\Program Files\Git\cmd\git.exe" add .
& "C:\Program Files\Git\cmd\git.exe" commit -m "Update Stick Clash"
& "C:\Program Files\Git\cmd\git.exe" push origin main
```

---

## 🧪 Automated Testing Suite

The repository includes a comprehensive `pytest` test suite verifying deterministic physics, damage calculations, guard breaks, parrying, status durations, Gauntlet upgrades, and room matchmaking:

```powershell
cd backend
& "venv/Scripts/pytest.exe" -v
```

### Test Coverage Summary:
- ✅ `test_combat.py`: Base damage, class damage multipliers, 70% guard reduction, 8-frame parry window, knockback formula scaling with missing health, and Rage Mode.
- ✅ `test_physics.py`: Deterministic AABB collision, double-jump limits, platform drop-through timer, and horizontal wrap-around.
- ✅ `test_statuses.py`: Burn and poison ticking damage, freeze diminishing returns (full -> half -> blocked), and shield damage absorption.
- ✅ `test_gauntlet.py`: 3-card upgrade drafting, stack caps, and Stone Golem boss phases every 5th level.
- ✅ `test_rooms.py`: 5-character alphabet room codes, Quick Match queue, and 5-second kill/assist attribution.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
