"""Centralized configuration for the Snake game.

Every tunable constant lives here so designers can tweak gameplay
without touching game logic.  Import ``CFG`` anywhere you need a value.
"""

import os
from dataclasses import dataclass, field
from typing import Tuple


# ---------------------------------------------------------------------------
# Direction helpers (shared by Snake, Food, GameEngine)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Direction:
    """Immutable 2-D offset used for movement vectors."""
    dx: int
    dy: int

    # Named constants
    UP    = None  # filled after class body
    DOWN  = None
    LEFT  = None
    RIGHT = None

    def opposite(self) -> "Direction":
        return Direction(-self.dx, -self.dy)

    def __eq__(self, other):
        if not isinstance(other, Direction):
            return NotImplemented
        return self.dx == other.dx and self.dy == other.dy

    def __hash__(self):
        return hash((self.dx, self.dy))


Direction.UP    = Direction(0, -1)
Direction.DOWN  = Direction(0,  1)
Direction.LEFT  = Direction(-1, 0)
Direction.RIGHT = Direction(1,  0)

DIRECTION_MAP = {
    "UP": Direction.UP,
    "DOWN": Direction.DOWN,
    "LEFT": Direction.LEFT,
    "RIGHT": Direction.RIGHT,
}


# ---------------------------------------------------------------------------
# Game-mode enum
# ---------------------------------------------------------------------------
class GameMode:
    HARD_WALLS = "hard_walls"
    WRAP_AROUND = "wrap_around"


# ---------------------------------------------------------------------------
# Main configuration dataclass
# ---------------------------------------------------------------------------
@dataclass
class Config:
    """All user-tweakable knobs in one place."""

    # -- Window / grid ------------------------------------------------------
    WINDOW_WIDTH: int = 800
    WINDOW_HEIGHT: int = 600
    GRID_SIZE: int = 20            # pixels per cell
    FPS: int = 60                  # render frame rate (physics decoupled)

    # -- Colours (R, G, B) --------------------------------------------------
    BG_COLOR: Tuple[int, int, int] = (18, 18, 24)
    BORDER_COLOR: Tuple[int, int, int] = (60, 60, 80)
    SNAKE_HEAD_COLOR: Tuple[int, int, int] = (80, 220, 100)
    SNAKE_BODY_COLOR: Tuple[int, int, int] = (50, 170, 70)
    SNAKE_BODY_ALT: Tuple[int, int, int] = (40, 140, 55)
    FOOD_COLOR: Tuple[int, int, int] = (220, 60, 60)
    GOLDEN_FOOD_COLOR: Tuple[int, int, int] = (255, 215, 0)
    TEXT_COLOR: Tuple[int, int, int] = (220, 220, 230)
    DIM_TEXT_COLOR: Tuple[int, int, int] = (120, 120, 140)
    ACCENT_COLOR: Tuple[int, int, int] = (100, 180, 255)
    DANGER_COLOR: Tuple[int, int, int] = (255, 70, 70)

    # -- Gameplay -----------------------------------------------------------
    INITIAL_SPEED: float = 8.0          # cells / second at game start
    SPEED_INCREMENT: float = 0.4        # added every SPEED_FOOD_INTERVAL foods
    SPEED_FOOD_INTERVAL: int = 5        # foods eaten between speed-ups
    MAX_SPEED: float = 22.0

    GOLDEN_FOOD_CHANCE: float = 0.12    # probability per spawn
    GOLDEN_FOOD_DURATION: float = 4.0   # seconds before it vanishes
    GOLDEN_FOOD_POINTS: int = 3
    REGULAR_FOOD_POINTS: int = 1

    INITIAL_SNAKE_LENGTH: int = 4
    INPUT_BUFFER_MAX: int = 2           # max queued direction changes

    # -- UI -----------------------------------------------------------------
    FONT_SIZE: int = 24
    TITLE_FONT_SIZE: int = 48
    SMALL_FONT_SIZE: int = 18

    # -- Persistence --------------------------------------------------------
    HIGH_SCORE_FILE: str = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), ".snake_highscore"
    )


# Singleton -- import this everywhere
CFG = Config()
