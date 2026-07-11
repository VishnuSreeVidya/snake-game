"""Food items -- regular apples and the timed golden apple.

``FoodManager`` owns both items and exposes helpers that the
``GameEngine`` calls each tick.
"""

import random
import time
from typing import List, Optional, Set, Tuple

from config import CFG


class FoodItem:
    """A single consumable on the grid."""

    __slots__ = ("pos", "is_golden", "spawn_time")

    def __init__(self, pos: Tuple[int, int], is_golden: bool = False) -> None:
        self.pos = pos
        self.is_golden = is_golden
        self.spawn_time = time.monotonic()

    @property
    def points(self) -> int:
        return CFG.GOLDEN_FOOD_POINTS if self.is_golden else CFG.REGULAR_FOOD_POINTS

    @property
    def expired(self) -> bool:
        if not self.is_golden:
            return False
        return (time.monotonic() - self.spawn_time) >= CFG.GOLDEN_FOOD_DURATION

    def __eq__(self, other):
        if not isinstance(other, FoodItem):
            return NotImplemented
        return self.pos == other.pos

    def __hash__(self):
        return hash(self.pos)


class FoodManager:
    """Manages spawning and lifetime of all food items."""

    def __init__(self, grid_w: int, grid_h: int) -> None:
        self.grid_w = grid_w
        self.grid_h = grid_h
        self.items: List[FoodItem] = []
        self._paused: bool = False
        self._pause_time: float = 0.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reset(self, snake_body: Set[Tuple[int, int]]) -> None:
        """Clear all food and spawn the first regular apple."""
        self.items.clear()
        self._spawn_regular(snake_body)

    def tick(self, snake_body: Set[Tuple[int, int]]) -> None:
        """Called once per game tick -- removes expired golden apples and
        ensures at least one regular apple exists."""
        # Expire golden apples
        self.items = [f for f in self.items if not f.expired]

        # Guarantee at least one regular food
        regulars = [f for f in self.items if not f.is_golden]
        if not regulars:
            self._spawn_regular(snake_body)

    def on_food_eaten(
        self, pos: Tuple[int, int], snake_body: Set[Tuple[int, int]]
    ) -> Optional[FoodItem]:
        """If *pos* matches a food item, remove it and return it (for
        scoring).  Otherwise return ``None``.

        After removal a new regular apple is always spawned; there is also
        a random chance to spawn a golden apple.
        """
        eaten: Optional[FoodItem] = None
        remaining: List[FoodItem] = []
        for f in self.items:
            if f.pos == pos and eaten is None:
                eaten = f
            else:
                remaining.append(f)
        self.items = remaining

        if eaten is None:
            return None

        # Always keep at least one regular food on the board
        regulars = [f for f in self.items if not f.is_golden]
        if not regulars:
            self._spawn_regular(snake_body)

        # Chance to spawn a golden apple (only one at a time)
        goldens = [f for f in self.items if f.is_golden]
        if not goldens and random.random() < CFG.GOLDEN_FOOD_CHANCE:
            self._spawn_golden(snake_body)

        return eaten

    def occupied_positions(self) -> Set[Tuple[int, int]]:
        return {f.pos for f in self.items}

    def pause(self) -> None:
        """Freeze all golden apple timers."""
        if not self._paused:
            self._paused = True
            self._pause_time = time.monotonic()

    def unpause(self) -> None:
        """Shift golden apple spawn times to account for paused duration."""
        if self._paused:
            elapsed = time.monotonic() - self._pause_time
            for f in self.items:
                if f.is_golden:
                    f.spawn_time += elapsed
            self._paused = False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _random_free_cell(self, snake_body: Set[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        """Find a random free cell using retry instead of full grid scan."""
        occupied = snake_body | self.occupied_positions()
        total = self.grid_w * self.grid_h
        if len(occupied) >= total:
            return None
        for _ in range(100):
            x = random.randrange(self.grid_w)
            y = random.randrange(self.grid_h)
            if (x, y) not in occupied:
                return (x, y)
        # Fallback: scan (rare, near-full grid)
        for x in range(self.grid_w):
            for y in range(self.grid_h):
                if (x, y) not in occupied:
                    return (x, y)
        return None

    def _spawn_regular(self, snake_body: Set[Tuple[int, int]]) -> None:
        pos = self._random_free_cell(snake_body)
        if pos is not None:
            self.items.append(FoodItem(pos, is_golden=False))

    def _spawn_golden(self, snake_body: Set[Tuple[int, int]]) -> None:
        pos = self._random_free_cell(snake_body)
        if pos is not None:
            self.items.append(FoodItem(pos, is_golden=True))
