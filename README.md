# Snake

A polished, portfolio-ready Snake game built with Python and Pygame.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Pygame](https://img.shields.io/badge/pygame-2.0%2B-green)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Features

| Feature | Description |
|---------|-------------|
| **Input Buffer** | Queues up to 2 rapid direction changes per tick -- no accidental self-collisions |
| **OOP Architecture** | Clean separation: `Config`, `Snake`, `Food`, `GameEngine` |
| **Dynamic Speed** | Difficulty ramps every 5 foods eaten (capped at a configurable max) |
| **Golden Apple** | Rare timed consumable (4 s) that awards triple points with a pulse animation |
| **Game Modes** | Toggle between **Hard Walls** (death on edge) and **Wrap-Around** (teleport) |
| **Persistent High Score** | Saved to a local file -- survives across sessions |
| **Clean UI** | Menu screen, pause overlay, death animation, HUD with score/length/speed |
| **Snake Eyes** | Head rendered with directional eyes for extra personality |
| **Fully Configurable** | Every constant (grid size, colours, speed, etc.) lives in `config.py` |

---

## Quick Start

```bash
# Install Pygame
pip install pygame

# Run the game
python main.py
```

---

## Controls

| Key | Action |
|-----|--------|
| `Arrow Keys` / `WASD` | Move snake |
| `Enter` / `Space` | Select / Confirm |
| `P` | Pause / Resume |
| `R` | Restart (on game over) |
| `ESC` | Back to menu / Quit |

---

## Project Structure

```
snake.py/
├── main.py            # Entry point
├── config.py          # All tunable constants (grid, colours, speed, etc.)
├── snake.py           # Snake entity with input buffer
├── food.py            # Food spawning (regular + golden apple)
├── game_engine.py     # Pygame loop, rendering, state management
├── .snake_highscore   # Persistent high score (auto-created)
├── .gitignore
└── README.md
```

---

## Configuration

Open `config.py` and edit the `Config` dataclass. Key knobs:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `WINDOW_WIDTH` / `WINDOW_HEIGHT` | 800 x 600 | Window dimensions |
| `GRID_SIZE` | 20 | Pixels per cell |
| `INITIAL_SPEED` | 8.0 | Starting cells/second |
| `SPEED_INCREMENT` | 0.4 | Speed added every N foods |
| `SPEED_FOOD_INTERVAL` | 5 | Foods between speed-ups |
| `MAX_SPEED` | 22.0 | Speed cap |
| `GOLDEN_FOOD_CHANCE` | 0.12 | Golden apple spawn probability |
| `GOLDEN_FOOD_DURATION` | 4.0 | Seconds before golden apple vanishes |
| `GOLDEN_FOOD_POINTS` | 3 | Points for golden apple |
| `INPUT_BUFFER_MAX` | 2 | Max queued direction changes |

---

## Architecture

- **`config.py`** -- Pure data. `Direction`, `GameMode`, and a `Config` dataclass holding every tunable value. Import `CFG` anywhere.
- **`snake.py`** -- Framework-agnostic `Snake` class. Owns the body list, a `deque`-based input buffer, and `advance()` / `grow()` methods. No Pygame imports.
- **`food.py`** -- Framework-agnostic `FoodManager`. Handles spawning logic (never on the snake), golden-apple lifetime, and removal on eat. No Pygame imports.
- **`game_engine.py`** -- The only module that imports Pygame. Owns the window, main loop, input routing, rendering, state machine, HUD, overlays, and high-score persistence.

---

## Requirements

- Python 3.8+
- Pygame 2.0+

```bash
pip install pygame
```

---

## License

MIT
