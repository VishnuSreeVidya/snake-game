<div align="center">

# 🐍 Snake

### *A modern, polished take on the classic Snake game*

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.0+-4F62CC?style=for-the-badge&logo=pygame&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-00C853?style=for-the-badge)

<br>

```
  ╔══════════════════════════════════╗
  ║    🍎  ● ● ● ●                  ║
  ║              ║                   ║
  ║              ▼                   ║
  ║          SCORE: 42               ║
  ║          HIGH: 108               ║
  ║          MODE: WRAP x2           ║
  ╚══════════════════════════════════╝
```

</div>

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🎮 Gameplay
- **Input Buffer** — Queue up to 2 rapid turns per tick, no accidental self-collisions
- **Dynamic Speed** — Difficulty ramps every 5 foods eaten
- **Golden Apple** — Rare timed consumable with pulse animation, 3x points
- **Two Game Modes** — **Hard Walls** or **Wrap-Around** (2x score, 30% faster)
- **Milestone Toasts** — Celebrations at score milestones (5, 10, 15...)

</td>
<td width="50%">

### 🛠 Technical
- **Clean OOP Architecture** — `Config`, `Snake`, `Food`, `GameEngine`
- **State Machine** — Menu, Playing, Paused, Game Over
- **Persistent High Score** — Survives across sessions
- **Death Animation** — Flashing snake on game over
- **Snake Eyes** — Directional eyes for extra personality
- **Fully Configurable** — Every constant in `config.py`

</td>
</tr>
</table>

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/VishnuSreeVidya/snake-game.git
cd snake-game

# 2. Install Pygame
pip install pygame

# 3. Play!
python main.py
```

---

## 🎹 Controls

| Key | Action |
|:---:|--------|
| `↑` `↓` `←` `→` / `W A S D` | 🐍 Move snake |
| `Enter` / `Space` | ✅ Select / Confirm |
| `P` | ⏸️ Pause / Resume |
| `R` | 🔄 Restart (game over) |
| `ESC` | 🏠 Back to menu / Quit |

---

## 📁 Project Structure

```
snake.py/
├── main.py            🚀  Entry point
├── config.py          ⚙️   All tunable constants
├── snake.py           🐍  Snake entity with input buffer
├── food.py            🍎  Food spawning (regular + golden)
├── game_engine.py     🎮  Pygame loop, rendering, state machine
├── .snake_highscore   🏆  Persistent high score (auto-created)
├── .gitignore
└── README.md          📖  You are here
```

---

## ⚙️ Configuration

Open `config.py` and edit the `Config` dataclass:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `WINDOW_WIDTH` × `WINDOW_HEIGHT` | 800 × 600 | Window dimensions |
| `GRID_SIZE` | 20 | Pixels per cell |
| `INITIAL_SPEED` | 8.0 | Starting cells/second |
| `SPEED_INCREMENT` | 0.4 | Speed added every N foods |
| `SPEED_FOOD_INTERVAL` | 5 | Foods between speed-ups |
| `MAX_SPEED` | 22.0 | Speed cap |
| `GOLDEN_FOOD_CHANCE` | 12% | Golden apple spawn rate |
| `GOLDEN_FOOD_DURATION` | 4.0s | Golden apple lifetime |
| `GOLDEN_FOOD_POINTS` | 3 | Points for golden apple |
| `INPUT_BUFFER_MAX` | 2 | Max queued direction changes |

---

## 🏗 Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  config.py  │────▶│  snake.py   │     │   food.py   │
│             │     │             │     │             │
│  Direction  │     │   Snake     │     │ FoodManager │
│  GameMode   │     │  - body     │     │  - spawn    │
│  Config     │     │  - buffer   │     │  - golden   │
└──────┬──────┘     │  - advance  │     │  - expire   │
       │            └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────┬───────┴───────────────────┘
                   ▼
          ┌─────────────────┐
          │ game_engine.py  │  🎮  The only Pygame module
          │                 │
          │  State Machine  │
          │  Rendering      │
          │  Input Routing  │
          │  HUD & Overlays │
          └────────┬────────┘
                   │
                   ▼
              main.py  🚀
```

- **`snake.py`** & **`food.py`** — Framework-agnostic, no Pygame imports, fully testable
- **`game_engine.py`** — The only module that imports Pygame
- **`config.py`** — Pure data, import `CFG` anywhere

---

## 📊 Game Modes

| | Hard Walls 🧱 | Wrap-Around 🌀 |
|---|:---:|:---:|
| **Edge behavior** | Death on contact | Teleport to opposite side |
| **Score multiplier** | ×1 | ×2 |
| **Speed** | Normal | +30% faster |
| **Difficulty** | Classic | High risk, high reward |

---

<div align="center">

### 🐍 Built with Python & Pygame

*Star ⭐ this repo if you enjoyed the game!*

</div>

---

## 📝 License

MIT License — feel free to fork, modify, and share!
