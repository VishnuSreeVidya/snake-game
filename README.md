# Snake 2.0 ⚡

A colorful terminal-based Snake game for Windows with rainbow visuals, milestones, and a persistent high score.

## Features

- Rainbow-colored snake body
- Animated food with various symbols
- 4 difficulty levels (Easy, Medium, Hard, INSANE)
- Floating `+1` popup animation when eating food
- Death animation (snake flashes red before game over)
- Blinking pause indicator
- Score milestones with toast notifications (`+1` popups, milestone messages like `🔥 5!`)
- Persistent high score (saved to `.snake_highscore`)
- Pause, restart, and quit controls
- Countdown before game start
- Game over screen with ASCII art

## Controls

| Key | Action |
|-----|--------|
| Arrow keys / WASD | Move |
| P | Pause / Resume |
| R | Restart |
| Q / Esc | Quit |

## Requirements

- Windows OS (uses `msvcrt`)
- Python 3.6+

## How to Run

```bash
python snake.py
```
