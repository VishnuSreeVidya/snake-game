# 🐍 Snake 2.0

A colorful terminal-based Snake game for **Windows** with rainbow visuals, multiple difficulty levels, animations, and persistent high scores.

![Python](https://img.shields.io/badge/python-3.6%2B-blue)
![Platform](https://img.shields.io/badge/platform-windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🎮 Features

| Feature | Description |
|---------|-------------|
| **Rainbow Snake** | Body segments cycle through vibrant colors |
| **4 Difficulty Levels** | Easy → Medium → Hard → INSANE |
| **Food Animations** | Floating `+1` popup drifts upward on eat |
| **Death Animation** | Snake flashes red before game over screen |
| **Blinking Pause** | Pause indicator toggles every 0.5s |
| **Score Milestones** | Toast notifications at 5, 10, 15, 20… |
| **High Score** | Persisted to `.snake_highscore` across sessions |
| **Game Over Art** | ASCII art screen with final stats |
| **Countdown** | 3… 2… 1… GO! before each game |

---

## 🎯 Difficulty Levels

| Key | Level | Speed | Feel |
|-----|-------|-------|------|
| `1` | Easy | 1 | Relaxed, great for beginners |
| `2` | Medium | 2 | Balanced default |
| `3` | Hard | 3 | Fast, needs quick reflexes |
| `4` | INSANE | 4 | Blazing fast — you've been warned |

Select at the **start screen** by pressing `1`–`4`, then press **Enter** to begin.

---

## ⌨️ Controls

| Key | Action |
|-----|--------|
| `↑ ↓ ← →` / `W A S D` | Move snake |
| `P` | Pause / Resume |
| `R` | Restart |
| `Q` / `Esc` | Quit |

---

## 🚀 Quick Start

```bash
python snake.py
```

That's it — no dependencies to install.

---

## 📋 Requirements

- **OS:** Windows (uses `msvcrt` for key input)
- **Python:** 3.6+
- **Terminal:** Any modern terminal that supports ANSI escape codes (Command Prompt, PowerShell, Windows Terminal)

---

## 📁 Project Structure

```
snake.py/
├── snake.py          # Main game
├── .snake_highscore  # Persistent high score (auto-created)
└── README.md
```

---

## 🛠️ How It Works

- The game renders a grid using **ANSI escape codes** directly to stdout — no curses or external libraries.
- Input is read with **`msvcrt.kbhit()` / `msvcrt.getch()`** for real-time non-blocking arrow key detection.
- Speed increases by `0.002s` per food eaten, capped at `0.05s`.
- High scores are saved to a local file in plain text.

---

## 💡 Tips

- The snake moves **faster vertically** (UP/DOWN) — the game accounts for taller terminal cells by doubling the sleep time on horizontal moves.
- Watch for the **milestone toasts** (`🔥 5!`, `🔥 10!`, …) that appear at the center of the screen.
- Use **P** frequently on Hard/INSANE modes to catch your breath.
