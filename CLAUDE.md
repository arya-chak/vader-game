# CLAUDE.md — Mask of Vader

## What this project is

A choice-driven tactical RPG following Darth Vader's psychological
transformation between Episodes III and IV. Players don't just play
*as* Vader — they *become* him through decisions that shape his
darkness, control, rage, and suppression. Inspired by KOTOR mechanics,
Force Unleashed power fantasy, and Oregon Trail consequence systems.

Built in Python. Terminal interface (Pygame removed/commented out).
Serious, gritty tone. Canonical accuracy is a hard requirement.

---

## Planning & implementation workflow

Planning (architecture, feature scoping, tradeoffs, design decisions)
happens in Claude.ai chat. All implementation — writing files, editing
code, running commands — happens here in Claude Code.

**For Claude Code:**
- Receive implementation briefs from the planning chat
- Act on them directly — the brief is the spec
- When a task is ambiguous, stop and ask rather than assume
- Flag anything that looks wrong or inconsistent with this file

**For the planning chat:**
- Never writes production code files
- Produces implementation briefs Claude Code can act on directly
- Flags CLAUDE.md updates needed before each handoff

**When to update this file:**
Any decision made in planning chat that affects how Claude Code should
behave — new conventions, confirmed behaviors, schema changes,
corrected assumptions — gets added here before the next Claude Code
session. This file is the handoff contract between the two contexts.

---

## Current repo state

### File structure
star-wars-vader/
├── src/
│   ├── character/
│   │   ├── vader.py              # Core character class
│   │   ├── suit_system.py        # 5-tier, 26-upgrade suit system
│   │   ├── force_powers.py       # 38 Force abilities
│   │   └── init.py
│   ├── combat/
│   │   ├── combat_system.py      # Turn-based combat engine
│   │   ├── boss_fight.py         # Boss phase/trigger/adaptive AI system
│   │   └── init.py
│   ├── story/
│   │   ├── init.py
│   │   ├── story_system.py       # Core story engine (537 lines)
│   │   └── opening_scenes.py     # Opening sequence (13 scenes, 650+ lines)
│   └── utils/
├── data/                         # (planned — JSON story content)
├── tests/
├── demo_combat.py
├── demo_story.py
├── main.py                       # Terminal game loop (Story → Combat → Next Scene)
└── CLAUDE.md

### What's built and working
- [x] Character system — `vader.py` (stats, psychology, leveling)
- [x] Suit system — `suit_system.py` (26 upgrades, Palpatine suspicion)
- [x] Force powers — `force_powers.py` (38 abilities, FP system)
- [x] Combat system — `combat_system.py` (turn-based, enemy AI, execution choices)
- [x] Boss fight system — `boss_fight.py` (phases, triggers, adaptive AI)
- [x] Story system — `story_system.py` (scenes, choices, flags, psychological tracking)
- [x] Opening sequence — `opening_scenes.py` (13 scenes, 6 branching paths)
- [x] Kyber Crystal mission — 40+ scenes, combat integration, Kirak Infil'a boss
- [x] Terminal game loop — Story → Combat → Next Scene flow tested and working
- [x] Terminal game loop (`main.py`) — exists but superseded; do not add features here
- [x] GUI entry point (`main_gui.py`) — active development target (Pygame)
- [ ] GUI fully functional — work in progress; planning chat will scope each screen
- [x] GUI entry point (`main_gui.py`) — active target; Pygame
- [x] `mask_hud.py` — visual rebuild complete; black background, two red oval lenses with glow + targeting grid, cyan title at top, menu in left eye, studio text in right eye
- [ ] Dialogue screen rebuild — planned after Mask HUD
- [ ] Save slot screen — low priority, style pass later

### What does NOT exist yet
- [ ] GUI (Pygame implementation — planned for Phase 2)
- [ ] Save/load system
- [ ] Mission system beyond Kyber Crystal arc
- [ ] Ollama AI integration
- [ ] Ship management screen

---

## Story system integration

**Entry point:** `main_gui.py` → `GUIGame`

**Lifecycle:**
- `self.vader`, `self.suit`, `self.story` are `None` until `start_new_game()` fires — never assume they exist at startup.
- `start_new_game(slot)` creates `DarthVader`, `SuitSystem`, `StorySystem(vader, suit)`, registers all scenes from `create_opening_scenes()`, then calls `_start_scene("the_void")`.
- `the_void` is always the first scene ID.

**Adapter:** `src/gui/utils/story_adapter.py` — `scene_to_gui(scene, available_choices)` converts a `Scene` object + filtered `Choice` list to the dict format `StoryDialogueScreen.set_scene()` expects.

**Portrait assignment rules (per dialogue line):**
- Speaker is `"Vader"` / `"Darth Vader"` → `left_portrait="vader_mask"`, `right_portrait=None`
- Speaker is `"Narrator"` / `"Inner Voice"` → both portraits `None`
- Any other speaker → `left_portrait="vader_mask"`, `right_portrait=<speaker_name_slugified>`

**Tags** are derived from `Choice` consequence fields: `darkness_change>0` → `[DARK SIDE]`, `<0` → `[LIGHT SIDE]`; `control_change>0` → `[CONTROL]`, `<0` → `[LOSS OF CONTROL]`; `rage_change>0` → `[RAGE]`.

**Auto-next scenes** (no choices): the adapter synthesises a single `{"id": "__continue__", ...}` choice. The choice callback detects `choice_id == "__continue__"` and calls `_start_scene(scene.auto_next)` directly — `make_choice` is NOT called.

**Double-start guard:** `make_choice` internally calls `start_scene` when `next_scene_id` is set. After `make_choice` returns, call `_load_scene_gui(next_scene_id)` only (not `_start_scene`), to avoid running `on_enter` twice.

---

## Tech stack

| Layer | Choice |
|---|---|
| Language | Python 3.11+, M1 Pro Mac |
| Terminal UI | `rich` library |
| GUI (future) | Pygame or Pyglet |
| AI integration (future) | Ollama (local, offline) |
| IDE | VS Code |
| Version control | GitHub |

---

## Core systems

### Character system (`vader.py`)

**Stats:**
- Physical: Strength (9), Dexterity (6), Constitution (8)
- Mental: Intelligence (8), Wisdom (5), Charisma (7)
- Force: Power (10), Control (6)
- Combat: Lightsaber Skill (10), Force Mastery (9)

**Psychological state (all 0–100):**
- **Darkness** — dark side alignment; affects available powers and story branches
- **Control** — emotional mastery; high = more options, low = ruled by rage
- **Suppression** — Anakin memories buried; affects flashback triggers
- **Rage** — current anger level; fuels power but clouds judgment

**Starting powers:** Force Push, Pull, Choke, Sense, Saber Throw, Force Persuasion

---

### Suit system (`suit_system.py`)

**26 upgrades across 5 tiers:**
- Tier 1 (Basic): 2–3 suspicion pts each — safe early game
- Tier 2 (Military-Grade): 5–7 pts — moderate risk
- Tier 3 (Advanced Prototype): 10–15 pts — significant risk
- Tier 4 (Experimental Sith Tech): 18–25 pts — includes Kyber-Enhanced Gauntlets (required for Force Lightning)
- Tier 5 (Forbidden): 30–40 pts — game-changing, likely triggers Palpatine loyalty test

**Palpatine suspicion system:**
- Upgrade too fast → unwinnable loyalty test
- Losing strips ALL upgrades; suit reset to basic
- Strategic pacing is core gameplay

**Component-by-component upgrades** — never wholesale improvements.

**Pain / suit damage:**
- Constant pain (40% baseline) fuels dark side power
- Suit damage reduces FP regen; breathing disruption adds 50% FP penalty

---

### Force powers (`force_powers.py`)

**38 powers across 6 categories:**
- Telekinesis (10): Push → Pull → Grip → Choke → Crush → Maelstrom + Force Unleashed additions
- Dark Side (11): Force Rage, Fear, Drain, Scream, **Force Lightning** (Kyber Gauntlets required, 30% suit damage risk), Lightning Bomb, Shield, Devastation
- Combat (8): Saber Throw → Barrier, Sith Strike, Aerial Assault, etc.
- Sense (3): Force Sense, Battle Meditation, Precognition
- Control (3): Force Barrier, Speed, Body
- Utility (3): Persuasion, Mind Probe, Force Cloak

**FP system:**
- Max FP: 100–200 (scales with level)
- Regen: 10–20 FP/turn (breathing disruption = 50% penalty)
- Rage bonus (≥80 rage): +5 FP/turn
- Force-sensitive kills: +10 FP
- Legendary spam (3+ uses): exhaustion debuff

---

### Combat system (`combat_system.py`)

**Vader's turn actions:** Attack, Force Power, Item, Defend, Move, Meditate (restore 30 FP, vulnerable), Retreat

**Enemy AI behaviors:** Aggressive, Defensive, Tactical, Calculated (droids), Panicked

**Execution choices (enemy <25% HP):**
1. Quick Kill [Neutral]
2. Force Choke Execution [+5 Darkness, terrorize enemies]
3. Brutal Dismemberment [+10 Darkness, -5 Control, mass terror]
4. Spare/Capture [-3 Darkness, +5 Control, possible intel]

**Combat duration targets:**
- Trash mobs: 2–4 turns
- Veterans/officers: 4–7 turns
- Boss fights: 8–15 turns

---

### Boss fight system (`boss_fight.py`)

**Key features:**
- Phase transitions triggered by HP thresholds (Phase 2 at 60%, Phase 3 at 30%, Final at 10%)
- Scripted events: `BossTrigger` fires once on HP threshold, turn number, or phase
- Adaptive AI: tracks Force vs melee usage, counters player pattern
- Scripted loss: `start_boss_fight(boss, scripted_loss=True)` — forces loss on condition

**Kirak Infil'a — First Duel** (scripted loss):
- 120 HP, 4 special actions, Form III (Soresu) defense
- Scripted loss: turn 8 OR Vader HP <30% → leg breaks, falls from mountain

**Kirak Infil'a — Final Duel** (winnable, two paths):
- Honor path (`water_tank_destroyed=False`): 150 HP, defense 18, HARD — Infil'a fully focused
- Massacre path (`water_tank_destroyed=True`): 120 HP, defense 12, EASY — Infil'a distracted saving civilians; +20 Darkness, +1000 civilians killed

**Integration pattern:**
```python
if scene.trigger_combat.get('boss_fight'):
    boss = create_infila_first_duel()
    boss_system.start_boss_fight(boss, scripted_loss=True)
else:
    combat_system.start_combat(enemies)
```

---

### Story system (`story_system.py` + `opening_scenes.py`)

**Scene structure:** `Scene(id, title, description, location, dialogue, choices)`

**Choice types:** Dialogue, Moral, Tactical, Relationship, Commitment

**Story flags:** Set via `state.set_flag("flag_name")`, checked via `state.has_flag(...)`, required on scene or choice via `requires_flags`

**Key opening flags:**
- `awakened`, `learned_padme_death`, `iconic_nooo`, `silent_grief`, `early_resentment`
- `suspects_truth`, `blames_jedi`, `first_mission_accepted`, `opening_complete`

**Story arcs (driven by psychological development):**
- Dark Lord, Conflicted, Redemption, Betrayal

**Opening sequence (13 scenes):**
Void → Awakening → (Rage/Control/Suppress path) → Palpatine Arrives →
(Iconic NOOO / Silent Grief / Blame Palpatine) → First Mission → Tutorial Complete

**Mid-combat pause/resume:** Boss fights pause at HP thresholds for story choices; boss state is preserved; difficulty adjusts based on player decision.

**Combat trigger pattern from story scenes:**
```python
scene.trigger_combat = {
    "enemy_types": [EnemyType.JEDI_SURVIVOR],
    "enemy_count": 1,
    "environment": "industrial_sector",
    "boss_fight": False  # True for boss encounters
}
```

---

## GUI rendering conventions

- Window: `pygame.FULLSCREEN` — actual size read from `pygame.display.get_surface().get_size()` after init. All layout measurements are proportional to `self.width` / `self.height`.
- Scene bg: 55.5% of height | Title bar: 6.7% | Dialogue: 26.7% | Choices: remainder
- Choices spacing is dynamic: available height divided evenly across choice count
- Reference resolution: 1600×900 (proportions hold at any fullscreen size)
- Draw order is always: background → structure → lenses → overlays → tint
- All alpha surfaces use `pygame.SRCALPHA`
- Left eye center: (530, 380) — menu options live here
- Right eye center: (1070, 380) — flavor text lives here
- Respirator: (800, 680)
- Color palette: see GUI Design Plan in project knowledge
- Fonts: SF Distant Galaxy (titles), ImperialCode (HUD/mono text), Times New Roman (dialogue)
- Font fallback: system Arial if .ttf files not found — always wrap font load in try/except
- Dialogue screen color palette: reddish-orange `(220,100,20)` for all border/accent elements — NOT cyan. Cyan is mask HUD only.
- Bottom panel has DS-style tech border: outer `(180,60,0)`, inner `(120,40,0)`, corner brackets in `(220,100,20)`, dividers at y=560 and y=800.
- Selected choice: bright gold `(255,180,0)` with vertical bar indicator (3px × 20px) drawn left of the chevron.

---

## Resources and materials

**Credits** — for upgrades and equipment  
**Materials:**
- Common: Durasteel, Electronics, Bacta
- Rare: Kyber Fragments (from Jedi kills)
- Very Rare: Ancient Artifacts (Sith temples)
- Rare: Prototype Components (Imperial R&D / black market)

**Imperial Favor** — required for reinforcements and some upgrades

**Reinforcements (limited use):**
- Stormtrooper Squad: -10 favor, 2-mission cooldown
- 501st Legion Unit: -15 favor, requires 501st rep >50
- Inquisitor: -20 favor, reports to Palpatine
- Orbital Strike: -25 favor, massive damage
- Overuse signals weakness to Palpatine

---

## Relationships

| Faction | Starting value | Notes |
|---|---|---|
| Palpatine | 50 | Complex master-servant; report to him to reset suspicion |
| Imperial Officers | 30 | Feared, not liked |
| Inquisitorius | 20 | Rivalry |
| 501st Legion | 80 | Former brothers-in-arms; know Vader's leadership style, not his identity |

The 501st recognizes Vader's leadership style without knowing his true identity — canonical consistency is required.

---

## GUI design (future — not yet implemented)

**Color palette:**
- Background: `#0a0a0a`
- Sith Red: `#cc0000`
- Imperial Blue: `#0088cc`
- Cyan/Active: `#00ffff`
- Dark Blue (secondary bg): `#1a4d6d`
- Gold (stats): `#ffaa00`

**Screens planned:**
1. Main Menu — Vader Mask HUD: black background, two red oval lenses with multi-layer glow + targeting grid, cyan SF Distant Galaxy title at top, menu options in left eye, studio credit in right eye. No structural framing panels — biometric readouts are reserved for the in-game HUD only.
2. Character Sheet — SWTOR-style tabbed (Character / Inventory / Equipment / Force Powers / Upgrades)
3. Dialogue Scene — Battlefront Elite Squadron style (portraits, text, choices)
4. Combat HUD — terminal-style with visual overlay
5. Ship Management — SWTOR holographic schematic style
6. Victory/Mission Complete screen

**Fonts:** SF Distant Galaxy, ImperialCode (Star Wars aesthetic); Times New Roman for dialogue (Return of the Jedi style)

**Resolution target:** 1920×1080

**`main_gui.py` is the active entry point.** All new feature work goes here.
Do not modify `main.py` unless explicitly asked — it's the terminal reference build.

---

## Canonical rules

- The 501st Legion knows Vader as their commander — not as Anakin Skywalker
- Kyber Crystal mission is based on canon Dark Times comics (Kirak Infil'a storyline)
- Force Lightning requires Kyber-Enhanced Gauntlets — never available without them
- Vader loses the first duel with Infil'a (scripted loss is canonical)
- Dark tone; no comedic or lighthearted story deviations

---

## Development principles

1. **Choices must have consequences** — short-term and long-term; no "correct" path
2. **Vader is powerful but constrained** — suit limitations and Palpatine's control are the challenge vectors
3. **Pain fuels power** — reducing pain reduces dark side strength (strategic tradeoff)
4. **Component-by-component progression** — never wholesale upgrades in a single step
5. **Canonical accuracy is non-negotiable** — draw from Legends comics for Dark Times content

---

# Coding Guidelines

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

For multi-step tasks, state a brief plan:

[Step] → verify: [check]
[Step] → verify: [check]
[Step] → verify: [check]


Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.