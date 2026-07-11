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

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _free_cells(self, snake_body: Set[Tuple[int, int]]) -> List[Tuple[int, int]]:
        occupied = snake_body | self.occupied_positions()
        return [
            (x, y)
            for x in range(self.grid_w)
            for y in range(self.grid_h)
            if (x, y) not in occupied
        ]

    def _spawn_regular(self, snake_body: Set[Tuple[int, int]]) -> None:
        free = self._free_cells(snake_body)
        if not free:
            return
        pos = random.choice(free)
        self.items.append(FoodItem(pos, is_golden=False))

    def _spawn_golden(self, snake_body: Set[Tuple[int, int]]) -> None:
        free = self._free_cells(snake_body)
        if not free:
            return
        pos = random.choice(free)
        self.items.append(FoodItem(pos, is_golden=True))
