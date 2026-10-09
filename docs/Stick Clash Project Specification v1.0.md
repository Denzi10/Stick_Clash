# Stick Clash: Project Specification

Version 1.0 | Concept frozen 9 October 2026 | Status: Approved for build

## 1. Document Overview

**Purpose.** This is the single source of truth for the design, technology and delivery of Stick Clash, a 2D online stickman platform brawler. It covers gameplay rules, numeric balance values, architecture, networking, content, schedule, testing and risks.

**Audience.** Developers, artists, sound designers and playtesters.

**Change control.** The concept is frozen. Any change must be logged as a change request (ID, description, impact on scope and schedule, decision) in Section 20. Numeric values in this document are launch defaults and may be tuned during balancing without a change request.

**Conventions.** Distances are in pixels on a virtual 1280x720 canvas. Time is in seconds unless stated. Frame data assumes 60 frames per second (f). MUST means required for v1.0, SHOULD means recommended, MAY means optional.

## 2. Product Vision

**Pitch.** Stick Clash is a fast online 2D platform brawler for up to four stickmen. Players fight across multi-tier arenas using melee combos, pickups, elemental status effects and a charged power move. A continuous Gauntlet mode chains levels together until a time or kill limit ends the run.

**Design pillars**

1. **Instant fun.** Join a match in under 10 seconds and learn the controls in two minutes.
2. **Readable chaos.** Effects are big and exciting, but every hit, status and team is clear at a glance.
3. **Comebacks always possible.** Knockback grows as health falls, and the power meter rewards taking hits.
4. **Juice.** Hit-stop, screen shake, slow-motion finishes and particles make every action feel strong.
5. **Endless variety.** Pickups, hazards, arenas and Gauntlet upgrades keep every match different.

**Target audience.** Players aged 12 to 30, friend groups, and streamers who want clippable moments. Casual to mid-core skill.

**Platforms.** Version 1.0 targets desktop browsers (Chrome, Edge, Firefox, Safari) with keyboard and gamepad support. Mobile touch controls are planned after launch.

**Inspirations.** Classic stickman fighting games, the multi-tier platform arenas of Snow Bros, and the knockback model of platform fighters.

## 3. Scope

**In scope for v1.0 (MUST)**

- Four game modes: Duel (1v1), Team Clash (2v2), Free-for-All (up to 4) and Gauntlet (continuous)
- Four fighter classes with one special move each
- Core moves: move, double jump, drop-through, light and heavy attack, air attack, dash, block, parry, grab and throw
- Health, power meter and Rage Mode
- Pickups: weapons, throwables, healing and power-ups
- Eight status effects
- Eight arenas with hazards
- Online rooms with shareable codes, quick match, and bot fill
- Gauntlet with objective levels, between-level upgrades, AI enemies and boss levels
- Full effects, audio, HUD, menus and settings

**Out of scope for v1.0**

- User accounts, ranked ladders and persistent progression
- Cosmetics shop and real-money transactions
- Custom arena editor, replays, spectator mode
- Mobile touch controls (planned as a follow-up)
- Voice or text chat (quick emotes only)

## 4. Game Modes

| Mode | Players | Respawn | Win condition | Default limits |
| --- | --- | --- | --- | --- |
| Duel | 1v1 | No | Best of 3 rounds; a round ends at zero health | Round timer 90 s |
| Team Clash | 2v2 | Yes, 3 s | Most team kills at time limit, or first team to the kill target | 5 min or 20 kills |
| Free-for-All | 2 to 4 | Yes, 3 s | Most kills at time limit, or first to the kill target | 5 min or 15 kills |
| Gauntlet | 1 to 4 | Mode specific | Highest total score when the run ends | Run limit set in lobby (Section 10) |

**Common rules**

- Respawn invulnerability lasts 2 seconds and ends early if the player attacks.
- Friendly fire is off in team modes. Friendly knockback is off.
- Ties at the time limit go to sudden death: the next kill wins.
- A player who disconnects is replaced by a bot after 20 seconds. Reconnecting within 20 seconds returns control.
- Kills are credited to the last enemy who damaged the target in the previous 5 seconds. A second damager in that window gets an assist.
- Hazard and fall deaths with no recent damager count as a self-KO and subtract 1 point of score.

## 5. Core Gameplay Systems

### 5.1 Controls (defaults)

| Action | Keyboard | Gamepad |
| --- | --- | --- |
| Move | A / D | Left stick |
| Jump / double jump | W or Space | A |
| Drop through platform | S (while on thin platform) | Down on stick |
| Light attack | J | X |
| Heavy attack | K | Y |
| Special | L | RB |
| Dash | U | RT |
| Block / parry | I | LT |
| Grab / pickup / throw | O | B |
| Emote wheel | E | D-pad |

All keys are remappable in Settings.

### 5.2 Movement

| Parameter | Value |
| --- | --- |
| Run speed | 300 px/s (scaled by class) |
| Ground acceleration | 3000 px/s squared |
| Air control | 70 percent of ground control |
| Gravity | 2200 px/s squared |
| Jump velocity | 820 px/s (about 150 px height) |
| Double jump velocity | 700 px/s |
| Maximum fall speed | 1000 px/s, or 1400 px/s with fast-fall (hold down) |
| Hurtbox size | 40 x 90 px (crouch and block 40 x 70) |
| Platform tier spacing | 150 to 170 px so one jump reaches the next tier |

Arenas MAY wrap horizontally: leaving one side re-enters from the other with momentum preserved.

### 5.3 Attacks

Frame data at 60 f/s. Damage is before class and status multipliers.

| Move | Startup | Active | Recovery | Damage | Base knockback (px/s) | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Light 1 | 4 f | 3 f | 8 f | 5 | 120 | Starts combo |
| Light 2 | 4 f | 3 f | 8 f | 5 | 120 | Cancel window 18 f |
| Light 3 | 6 f | 4 f | 10 f | 8 | 260 | Combo finisher, launches |
| Heavy | 14 f | 5 f | 18 f | 16 | 520 | Hold up to 0.6 s to charge for up to +50 percent damage |
| Air attack | 5 f | 4 f | 10 f | 9 | 300 | Horizontal arc |
| Down-air slam | 8 f | 6 f | 14 f | 12 | 350 | Spikes target downward |
| Dash attack | 6 f | 5 f | 12 f | 10 | 380 | Cannot be used during dash cooldown |
| Throw | 8 f | 2 f | 14 f | 8 | 400 | Cannot be blocked |

### 5.4 Damage, knockback and hit-stun

- Final damage = move damage x attacker class multiplier x attacker status multiplier x (1 minus target block reduction if blocking).
- Launch speed = base knockback x (1 + 1.5 x (1 minus current health divided by max health)) divided by target weight.
- Hit-stun = 0.10 s + launch speed divided by 4000, capped at 0.5 s.
- Attacks hit each target at most once per swing.
- Hit-stop: both attacker and target freeze for 3 f on light hits, 6 f on heavy hits and 10 f on finishing blows.
- Combo scaling: each hit in a combo beyond the third reduces damage by 10 percent, to a minimum of 50 percent. Combos reset after 1.5 s without a hit.

### 5.5 Dash, block and parry

- **Dash.** Moves 200 px in 0.16 s. The first 0.12 s are invulnerable. Cooldown 1.0 s. A dash cancels any attack recovery.
- **Block.** Hold to reduce incoming damage by 70 percent and cut knockback by 60 percent. Blocking uses a guard meter of 40. Damage taken while blocking drains it, and it regenerates at 15 per second when not blocking. At zero the guard breaks and the player is stunned for 1.2 s.
- **Parry.** Pressing block within the first 8 f of a hit negates damage, stuns the attacker for 0.7 s and grants 10 power. Throws and hazards cannot be parried.

### 5.6 Health, KO and respawn

- Health is 100 by default (varies by class). No passive regeneration except during Rage Mode.
- A fighter is KO'd at zero health and collapses as a ragdoll for 1 s before respawning, if the mode allows it.
- Respawn points are chosen as the spawn farthest from enemies at the moment of respawn.

### 5.7 Power meter and Rage Mode

- The meter ranges from 0 to 100.
- Gain: 0.6 per point of damage dealt, 0.4 per point of damage taken, 10 per successful parry, 40 from an Energy Drink pickup.
- The meter never drains over time and resets on KO to 25.
- **Special move:** costs 50 power (cost drops to 25 during Rage).
- **Rage Mode:** costs 100 power and lasts 8 s. Grants +30 percent damage, +15 percent speed, 2 health per second regeneration, and an aura effect. Rage cannot be reactivated until the meter refills.

## 6. Fighter Classes

Players choose a class in the lobby. In Gauntlet the class is locked for the whole run.

| Class | Health | Speed | Damage x | Weight | Passive | Special (cost 50) |
| --- | --- | --- | --- | --- | --- | --- |
| Brawler | 100 | 300 | 1.0 | 1.0 | +10 max guard | **Quake Slam:** leap and slam, 20 damage, 180 px radius, knockdown 0.8 s, cooldown 6 s |
| Ninja | 85 | 345 | 0.9 | 0.85 | Extra air dash (one per jump) | **Shadow Dash:** dash 320 px through enemies, 14 damage, cooldown 6 s |
| Mage | 80 | 285 | 0.95 | 0.9 | Arcane Bolt: ranged light attack, 4 damage, 0.5 s cooldown | **Elemental Blast:** projectile 16 damage, 600 px range, applies burn or freeze alternately, cooldown 5 s |
| Bruiser | 130 | 255 | 1.2 | 1.3 | Super armor during heavy attack startup | **Charge Tackle:** rush 260 px carrying enemies, 18 damage, stun 0.5 s, cooldown 7 s |

## 7. Pickups and Weapons

### 7.1 Spawn rules

- A crate drops from the top of the arena every 8 to 12 seconds. A maximum of 3 pickups may exist at once.
- Rarity: common 60 percent, rare 30 percent, epic 10 percent. Epic items are power-ups and the Hammer.
- Fixed weapon spawn points on arenas respawn their item 20 seconds after it is taken.
- Pickups despawn after 20 seconds if untouched and blink for the last 4 seconds.

### 7.2 Melee and ranged weapons

A held weapon replaces light and heavy attacks. It breaks when durability runs out. Players drop it with the grab button or throw it for half of its damage.

| Weapon | Damage | Durability | Range | Notes |
| --- | --- | --- | --- | --- |
| Sword | 12 | 20 hits | 70 px | Fast, balanced |
| Bat | 10 | 18 hits | 65 px | Knockback x1.4 |
| Hammer | 20 | 10 hits | 80 px | Slow, ground shockwave, epic |
| Nunchucks | 6 | 30 hits | 55 px | Very fast four-hit chain |
| Spear | 11 | 20 hits | 120 px | Long reach, slow recovery |
| Bow | 9 | 8 arrows | 700 px/s arrow | Hold to charge, up to +50 percent damage |
| Pistol | 6 | 12 shots | 900 px/s bullet | 3 shots per second |
| Boomerang | 8 | Unlimited | 400 px out and back | Only one in flight at a time |

### 7.3 Throwables, healing and power-ups

| Item | Effect |
| --- | --- |
| Bomb | 1.5 s fuse, 25 damage, 140 px radius |
| Banana peel | Target slips and is stunned for 1 s |
| Snowball | 4 damage and slow |
| Frost orb | Freezes the target |
| Sticky trap | Slow zone on the ground for 4 s |
| Health pack | +30 health and removes burn and poison |
| Energy drink | +40 power |
| Speed boost (10 s) | +30 percent move speed |
| Double damage (10 s) | +100 percent damage dealt |
| Shield bubble (8 s) | Absorbs 30 damage |
| Giant (8 s) | 1.5x size, +20 percent damage, +30 temporary health |
| Ghost (6 s) | Enemies see the fighter at 30 percent opacity |

Timed items run from the moment of pickup, and picking up a new power-up replaces the current one.

## 8. Status Effects

| Status | Effect | Duration | Counterplay |
| --- | --- | --- | --- |
| Burn | 3 damage per second | 4 s | Health pack, or dash through water tiles |
| Freeze | Frozen in place, takes +20 percent damage, shatters on a heavy hit | 1.5 s | Mash jump to break out 0.4 s sooner |
| Shock | Stun 0.6 s and chains 5 damage to fighters within 150 px | Instant | Block reduces stun to 0.3 s |
| Poison | 2 damage per second | 6 s | Health pack |
| Slow | Move speed reduced by 40 percent | 3 s | Dash |
| Stun | Cannot act | 0.4 to 1.2 s (source dependent) | Parry prevents it |
| Shield | Absorbs damage before health | 6 to 8 s | Break with heavy attacks |
| Rage / Haste | Boosted damage or speed | 6 to 10 s | Avoid and kite |

**Rules**

- Reapplying a status refreshes its duration and does not stack its intensity.
- Freeze has diminishing returns: a second freeze within 5 seconds lasts half as long, and a third is blocked.
- Each status shows an icon above the fighter with a shrinking ring for remaining time.
- Statuses are cleared on KO.

## 9. Arenas and Hazards

### 9.1 Launch arenas

| Arena | Theme | Special feature | Best modes |
| --- | --- | --- | --- |
| Snow Peaks | Icy mountains | Slippery floors (friction 0.3), snow piles | All |
| Volcano Pit | Lava cavern | Lava rises 40 px every 20 s and resets | FFA, Gauntlet |
| Neon City | Rooftops | Moving platforms on fixed paths | Team Clash |
| Jungle Ruins | Temple | Bounce mushrooms (launch 1000 px/s) | FFA |
| Sky Islands | Floating rocks | Wind gusts push fighters, platforms crumble after 2 s | Team Clash |
| Factory Floor | Industrial | Conveyor belts and crushers | Gauntlet |
| Crystal Cave | Caverns | Falling stalactites with a 1 s warning shadow | FFA |
| Training Dojo | Plain | No hazards, symmetric layout | Duel |

Arenas are multi-tier (3 to 4 tiers) in the style of the reference screenshot, with open gaps in the centre, spawn points on both sides, and optional horizontal wrap-around. Standard size is 1280x720. Larger arenas (1600x900) use a camera that tracks all players and zooms out to fit them.

### 9.2 Hazards

| Hazard | Effect |
| --- | --- |
| Spikes | 15 damage and a small knock-up, 1 s immunity after contact |
| Lava | 8 damage per second plus burn |
| Bounce pad | Launches upward at 1000 px/s |
| Conveyor belt | Moves fighters at 120 px/s |
| Crusher | 30 damage, telegraphed with a 1 s warning |
| Wind | 150 px/s horizontal push, direction shown by particles |
| Falling block | 20 damage, telegraphed with a shadow |

### 9.3 Arena data format

Each arena is a JSON file with these fields: id, name, size (width, height), wrap flag, background layers, platforms (position, size, type solid or thin or moving, path), spawn points (team tag optional), pickup spawn points (item type or random), hazards (type, position, parameters), and music track. The same file is loaded by the client for display and by the server for collision.

## 10. Gauntlet (Continuous) Mode

### 10.1 Run settings

- Players: 1 to 4. Variants: **Versus** (teams or free-for-all) and **Co-op** (players against AI).
- Run limit chosen in the lobby: a total time (5, 10 or 15 minutes), a total kill target (25, 50 or 100), or both with whichever comes first ending the run.
- Each level has its own objective and its own limit. When a level ends, the next arena loads immediately.

### 10.2 Level flow

1. Level loads with a 3 s countdown.
2. Players fight until the level objective or level timer completes.
3. A 5 s results screen shows level score and kills.
4. Each player picks one of three random upgrades within 10 s (random pick on timeout).
5. Next level starts. Return to step 1 until the run limit is reached.
6. A final results screen ranks players or teams by total score.

### 10.3 Level objectives

| Objective | Rule | Level limit |
| --- | --- | --- |
| Kill count | First player or team to 10 kills | 120 s |
| Timed score | Most kills when the timer ends | 90 s |
| Last standing | Eliminate all rivals, no respawn | 120 s |
| King of the Hill | Hold a moving zone for 45 cumulative seconds | 150 s |
| Survival (Co-op) | Defeat all waves, shared lives | 180 s |
| Boss | Defeat the boss, appears every 5th level | 240 s |

Objective choice is weighted random, avoiding the same objective twice in a row. Difficulty tier equals the level number divided by 5, rounded up, and raises enemy health, speed and aggression by 10 percent per tier.

### 10.4 Scoring

| Event | Points |
| --- | --- |
| Kill | +100 |
| Assist | +25 |
| Level win | +200 |
| Speed bonus | Up to +100, proportional to remaining level time |
| Kill streak of 3 / 5 / 7 | +50 / +100 / +150 |
| Death (Versus) | minus 25 |
| Boss defeated | +500 split by damage dealt |

In Co-op, players share a pool of 6 lives. A downed player can be revived by a teammate standing nearby for 3 seconds. The run ends when the pool is empty and all players are down.

### 10.5 Upgrade pool

Upgrades last for the rest of the run and stack up to the cap shown.

| Upgrade | Effect | Cap |
| --- | --- | --- |
| Heavy Hitter | +10 percent damage | x3 |
| Thick Skin | +15 max health | x3 |
| Quick Feet | +8 percent move speed | x3 |
| Power Surge | +20 percent power meter gain | x3 |
| Second Wind | Once per level, survive a lethal hit at 30 health | x1 |
| Vampiric | Heal 5 percent of damage dealt | x2 |
| Long Arm | +10 percent attack range | x2 |
| Lucky Crates | Better item rarity near you | x2 |
| Dash Master | Dash cooldown reduced by 20 percent | x2 |
| Iron Guard | +20 guard meter | x2 |
| Elemental Touch | 10 percent chance to apply burn on hit | x2 |
| Magnet Hands | Auto-collect items within 150 px | x1 |

### 10.6 AI enemies and boss

- **Enemy types:** Grunt (melee, balanced), Archer (ranged, keeps distance), Brute (slow, heavy, super armor), Ninja minion (fast, dodges).
- AI uses a finite state machine: idle, chase, attack, retreat, stunned. It reads the same game state as players and uses no hidden information.
- Bots that fill empty player slots use the same AI with reduced aggression and are selectable as Easy, Normal or Hard.
- **Stone Golem boss:** health 1200 plus 400 per extra player. Attacks: ground slam, boulder throw, shockwave. Phases at 66 percent and 33 percent health add faster attacks and falling rocks. A health pack and an epic item drop at each phase change.

## 11. UI and UX

**Screens:** Title, Mode Select, Lobby (room code, class pick, ready state, bot toggles), Loading, In-Game HUD, Upgrade Pick, Results, Settings, Controls and Tutorial.

**HUD elements**

- Health bar and power meter for each fighter, colour-coded by team
- Status icons above fighters
- Kill counter or team score, match timer and objective tracker
- Combo counter and floating damage numbers
- Kill feed in the top-right corner
- Ping indicator and a quick emote wheel

**Flow.** Title, then Mode Select, then Lobby (Quick Match, Create Room or Join by Code), then Match, then Results, then back to the Lobby with the same group.

**Accessibility.** Colour-blind-safe team palettes plus a shape marker above each fighter, a screen-shake slider, a reduce-flashing toggle, remappable controls, and adjustable HUD size.

**Tutorial.** A 60-second interactive tutorial against a training dummy teaches movement, attacks, blocking, dash and pickups on first launch, and is skippable.

## 12. Art, Effects and Audio

**Character art.** Stickmen are procedurally drawn from line segments with simple inverse kinematics and ragdoll on KO. This keeps assets tiny and gives a distinctive look. Each team and player has a bold colour, glow outline and optional hat or accessory.

**Backgrounds.** Hand-drawn doodle or paper-cut style layered with parallax. Each arena has 3 layers: sky, far, and near decoration.

**Effects list (MUST)**

- Hit-stop, screen shake, camera zoom on heavy hits, and slow-motion on the final kill of a match
- Impact sparks, ink splatters (no blood), weapon trails, dash afterimages and jump dust
- Elemental effects: fire, ice shards, lightning arcs and poison bubbles
- Rage Mode aura, shield bubble, giant-size ripple
- Ragdoll KO and respawn flash

**Audio.** Punchy short sound effects for each action, chiptune-style music loops per arena, and dynamic music that adds layers during Rage Mode and the final 30 seconds of a level. Announcer lines are text-only in v1.0.

## 13. Technical Architecture

### 13.1 Technology stack

| Layer | Choice | Reason |
| --- | --- | --- |
| Language | TypeScript across client, server and shared code | One language and shared types |
| Rendering | Phaser 3 (WebGL, canvas fallback) | Mature 2D engine, used for rendering and input only |
| Build | Vite | Fast builds, small bundles |
| Game simulation | Custom lightweight AABB physics in a shared package | Deterministic, runs on both client and server |
| Multiplayer | Node.js 20 with Colyseus | Rooms, matchmaking and state sync built in |
| Hosting | Single region first (closest to players), containerised | Low cost, easy to add regions |
| Optional storage | Redis for room discovery, PostgreSQL after v1.0 | Leaderboards come later |

### 13.2 Structure

- **client:** Phaser scenes, input, rendering, audio, UI, prediction.
- **server:** Colyseus rooms, matchmaking, bot AI, anti-abuse checks.
- **shared:** game simulation (movement, combat, statuses, items), constants, arena loader, message types.
- **content:** arena JSON, item and upgrade definitions, balance tables.

The simulation lives in the shared package so the server is authoritative and the client can predict the local player using the identical code.

### 13.3 Performance targets

- Client 60 f/s on a mid-range integrated GPU laptop, with a 30 f/s floor on low-end Chromebooks.
- Initial download under 5 MB compressed, playable within 10 seconds on a typical 4G connection.
- Server: one room costs well under 2 percent of a vCPU, with a target of 50 concurrent rooms per vCPU (to be validated by load tests).

## 14. Networking Specification

- **Server simulation:** fixed 60 Hz tick.
- **Snapshots:** broadcast to clients at 20 Hz using delta compression.
- **Client input:** sent every client frame as a sequence number, tick and a bitmask of keys. The server buffers 2 ticks of input to smooth jitter.
- **Prediction:** the client simulates the local player immediately and reconciles against server snapshots, replaying unacknowledged inputs.
- **Interpolation:** remote players and entities are rendered 100 ms in the past, interpolated between snapshots.
- **Lag compensation:** the server keeps 200 ms of hurtbox history and rewinds up to 100 ms when resolving melee and projectile hits.
- **Events:** hits, KOs, pickups and status changes are sent as discrete events, so effects play at the right moment even between snapshots.
- **Supported latency:** playable up to 150 ms round trip. A warning icon appears above 150 ms.
- **Reconnection:** the slot is held for 20 seconds, then a bot takes over.

### Message overview

| Direction | Message | Contents |
| --- | --- | --- |
| Client to server | join | Nickname, class, room code or quick-match flag |
| Client to server | input | Sequence, tick, key bitmask |
| Client to server | ready / emote | Lobby ready state, emote id |
| Server to client | snapshot | Player states, entities, hazards, scores, tick |
| Server to client | event | Hit, KO, pickup, status, level change, upgrade offer |
| Server to client | lobby | Roster, settings, countdown |
| Server to client | result | Match or level summary |

### Security and abuse prevention

- Clients send only inputs. The server alone decides damage, positions, items and scores.
- Input rate limit of 120 messages per second per client, with invalid messages dropped.
- Secure WebSocket (WSS), strict origin checks, and rate limits on room creation.
- Nicknames pass a profanity filter and a length limit of 16 characters.
- Room codes are 5 characters from a 32-character alphabet (no look-alike characters).

## 15. Data Models

**Player state:** id, nickname, class, team, position, velocity, facing, action state, animation frame, health, max health, power, guard, statuses (type and remaining time), held weapon (type and durability), upgrades, score, kills, deaths, assists.

**Match config:** mode, arena list or single arena, kill target, time limit, team assignment, bot slots with difficulty, Gauntlet run limit and variant, seed for item spawns.

**Item definition:** id, category, rarity, damage, durability or ammo, range, effect, sprite and sound ids.

**Upgrade definition:** id, name, description, stat modifier, stack cap.

**Status definition:** id, duration, tick rate, damage per tick, stacking rule, icon, effect reference.

All definitions live in content files and are loaded by both client and server, so balance changes need no code changes.

## 16. Non-Functional Requirements

| Area | Requirement |
| --- | --- |
| Browsers | Latest two versions of Chrome, Edge, Firefox and Safari on desktop |
| Input | Keyboard and standard gamepads |
| Availability | Server restarts must not exceed 1 minute and should not drop active matches during planned deploys where possible |
| Stability | At least 99 percent of sessions free of client crashes |
| Scalability | Add rooms by adding server instances behind a load balancer |
| Privacy | No personal data collected in v1.0, only a chosen nickname per session |
| Maintainability | Shared types, unit tests on simulation code, content-driven balance |
| Localisation | UI strings are kept in a table to allow translation after v1.0 |

## 17. Development Roadmap

Estimates assume one developer working about 15 to 20 hours per week. Adjust if more people join.

| Milestone | Weeks | Deliverables |
| --- | --- | --- |
| M1 Foundation | 1 to 2 | Repository, shared simulation skeleton, one stickman moving and jumping in one arena |
| M2 Core combat | 3 to 5 | Light, heavy and air attacks, knockback, hit-stop, block, parry, dash, health, power meter |
| M3 Online | 6 to 8 | Colyseus rooms, lobby, prediction and interpolation, four players, bots, room codes |
| M4 Content I | 9 to 10 | Pickups, weapons, status effects, four classes, three arenas |
| M5 Modes | 11 to 12 | Duel, Team Clash, Free-for-All, scoring, results, remaining arenas and hazards |
| M6 Gauntlet | 13 to 15 | Level chaining, objectives, upgrades, AI enemies, boss |
| M7 Polish | 16 to 17 | Full effects, audio, HUD, menus, settings, tutorial, accessibility options |
| M8 Beta and launch | 18 to 20 | Closed playtests, balancing, load tests, deployment, portal and community launch |

A playable local prototype with two fighters SHOULD exist by the end of week 5 to validate that combat feels good before building online features.

## 18. Testing and Quality Assurance

- **Unit tests** on damage, knockback, statuses, scoring and upgrade stacking in the shared simulation.
- **Determinism tests:** the same input sequence must produce the same state on client and server.
- **Network simulation** at 50, 100 and 150 ms latency with 2 percent packet loss, checking prediction errors and visible rubber-banding.
- **Load test** with 100 simulated rooms of bots to validate server capacity.
- **Playtests:** at least three rounds with 8 to 12 players each. Measure time to first match (target under 30 s), average match length (target 3 to 5 min), and how often players choose to play again.
- **Balance targets:** each class wins 45 to 55 percent of mirrored-skill matches, and no single weapon accounts for more than 25 percent of kills.
- **Bug severity:** Critical (crash or exploit, fix immediately), Major (broken feature, fix before milestone end), Minor (visual or polish issue, scheduled).

## 19. Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Netcode feels laggy | Medium | High | Prediction, interpolation, small rooms, early network testing in M3 |
| Combat lacks feel | Medium | High | Prototype locally first, focus on hit-stop and effects, frequent playtests |
| Scope too large for one developer | High | High | Strict milestones, ship Duel first, cut classes or arenas before cutting polish |
| Balance problems | Medium | Medium | Content-driven tables, telemetry on kills per weapon and class |
| Cheating | Low | Medium | Server-authoritative design and input validation |
| Low player count at launch | High | High | Bots fill empty slots, room codes for friends, share clips, portal submissions |
| Hosting cost growth | Low | Medium | Low per-room cost, autoscaling, single region at start |

## 20. Open Items, Change Log and Future Work

**Open items to settle early**

- Final game title (working title: Stick Clash)
- Whether stickmen stay pure line art or gain simple cartoon details
- Which free asset sources or composers to use for sound
- Hosting provider and region

**Change log**

| ID | Date | Change | Decision |
| --- | --- | --- | --- |
| CR-000 | 9 Oct 2026 | Concept frozen at v1.0 | Approved |

**Future work (post v1.0)**

- Mobile touch controls
- Accounts, ranked ladder and persistent progression
- Cosmetics and seasonal events
- Custom arena editor and community maps
- Replays, clip export and spectator mode
- More classes, weapons and Gauntlet bosses
- Localisation

## Appendix A. Glossary

| Term | Meaning |
| --- | --- |
| Hurtbox | Area where a fighter can be hit |
| Hit-stop | Brief freeze on impact to give attacks weight |
| Knockback | Distance and speed a fighter is launched when hit |
| Parry | Perfectly timed block that stuns the attacker |
| Rage Mode | Temporary power state unlocked by a full power meter |
| Gauntlet | Continuous mode that chains levels until a run limit ends |
| Server-authoritative | The server decides all game outcomes, and clients only send inputs |
| Client-side prediction | Client simulates the local player instantly, then corrects against the server |
| Interpolation | Smoothly rendering other players between received snapshots |

## Appendix B. Acceptance Criteria for v1.0

1. A new player can join a Quick Match and be fighting within 10 seconds.
2. Four players can play a full match online with no desyncs at 100 ms latency.
3. All four modes work end to end, including results screens.
4. All four classes, eight weapons, five throwables, six healing or power-up items, eight statuses and eight arenas are playable.
5. Gauntlet chains at least 10 levels, including two boss levels, with upgrade picks between levels.
6. Run limits by time and by kill count both end a Gauntlet run correctly.
7. Bots can fill any empty slot and take over after a disconnect.
8. Effects, audio and HUD meet the lists in Sections 11 and 12.
9. Performance targets in Section 13.3 are met on the reference test devices.
10. All acceptance tests in Section 18 pass and no Critical or Major bugs remain open.
