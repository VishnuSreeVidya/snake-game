"""Snake entity -- owns its body, direction, and an input buffer.

The input buffer is a small deque that queues up to
``Config.INPUT_BUFFER_MAX`` directional changes between ticks so that
rapid key-presses are resolved one-per-tick instead of causing accidental
self-collisions.
"""

from collections import deque
from typing import Deque, List, Tuple

from config import CFG, Direction, DIRECTION_MAP


class Snake:
    """Represents the player-controlled snake on the grid."""

    def __init__(self, grid_w: int, grid_h: int) -> None:
        self.grid_w = grid_w
        self.grid_h = grid_h
        self.body: List[Tuple[int, int]] = []
        self.direction: Direction = Direction.RIGHT
        self._input_buffer: Deque[Direction] = deque(maxlen=CFG.INPUT_BUFFER_MAX)
        self.grow_pending: int = 0
        self.reset()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Place the snake at the centre of the grid heading right."""
        cx = self.grid_w // 2
        cy = self.grid_h // 2
        self.body = [
            (cx - i, cy) for i in range(CFG.INITIAL_SNAKE_LENGTH)
        ]
        self.direction = Direction.RIGHT
        self._input_buffer.clear()
        self.grow_pending = 0

    def queue_direction(self, name: str) -> None:
        """Push a named direction onto the input buffer.

        The buffer is consumed one entry per tick in ``advance()``.
        """
        new_dir = DIRECTION_MAP.get(name.upper())
        if new_dir is None:
            return

        # Determine the "effective current direction" -- either the
        # direction already queued (tail of buffer) or the live direction.
        effective = self._input_buffer[-1] if self._input_buffer else self.direction

        # Reject 180-degree reversals and no-ops.
        if new_dir == effective or new_dir == effective.opposite():
            return

        if len(self._input_buffer) < CFG.INPUT_BUFFER_MAX:
            self._input_buffer.append(new_dir)

    def advance(self, wrap: bool = False) -> Tuple[Tuple[int, int], bool]:
        """Move the snake one cell.

        Returns ``(new_head, alive)`` where *alive* is ``False`` when the
        snake collides with itself or a wall (in hard-wall mode).
        """
        # --- consume one buffered direction change ----------------------
        if self._input_buffer:
            self.direction = self._input_buffer.popleft()

        dx, dy = self.direction.dx, self.direction.dy
        hx, hy = self.body[0]
        nx, ny = hx + dx, hy + dy

        # --- wall handling ---------------------------------------------
        if wrap:
            nx %= self.grid_w
            ny %= self.grid_h
        else:
            if nx < 0 or nx >= self.grid_w or ny < 0 or ny >= self.grid_h:
                return (nx, ny), False

        # --- self-collision -------------------------------------------
        if (nx, ny) in self.body[:-1]:
            return (nx, ny), False

        self.body.insert(0, (nx, ny))

        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

        return (nx, ny), True

    def grow(self, amount: int = 1) -> None:
        """Queue *amount* extra segments to be added on future advances."""
        self.grow_pending += amount

    @property
    def head(self) -> Tuple[int, int]:
        return self.body[0]

    @property
    def length(self) -> int:
        return len(self.body)
