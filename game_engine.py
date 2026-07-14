"""GameEngine -- owns the Pygame window, main loop, rendering, and state.

This is the only module that imports ``pygame``; every other module stays
framework-agnostic so it can be tested or re-used without Pygame.
"""

import math
import time
from typing import Optional

import pygame

from config import CFG, Direction, GameMode
from snake import Snake
from food import FoodManager


# ------------------------------------------------------------------
# Game states
# ------------------------------------------------------------------
class State:
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"


# ------------------------------------------------------------------
# Engine
# ------------------------------------------------------------------
class GameEngine:
    """Top-level controller: window, loop, input, rendering, state."""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(
            (CFG.WINDOW_WIDTH, CFG.WINDOW_HEIGHT)
        )
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()

        # Fonts
        self.font = pygame.font.SysFont("consolas", CFG.FONT_SIZE)
        self.title_font = pygame.font.SysFont("consolas", CFG.TITLE_FONT_SIZE, bold=True)
        self.small_font = pygame.font.SysFont("consolas", CFG.SMALL_FONT_SIZE)

        # Derived grid dimensions (reserve 40px at bottom for HUD)
        self.HUD_HEIGHT = 40
        self.cols = CFG.WINDOW_WIDTH // CFG.GRID_SIZE
        self.rows = (CFG.WINDOW_HEIGHT - self.HUD_HEIGHT) // CFG.GRID_SIZE
        self.grid_pixel_h = self.rows * CFG.GRID_SIZE

        # Entities
        self.snake = Snake(self.cols, self.rows)
        self.food = FoodManager(self.cols, self.rows)

        # State
        self.state = State.MENU
        self.score = 0
        self.high_score = self._load_high_score()
        self.game_mode = GameMode.HARD_WALLS
        self.speed = CFG.INITIAL_SPEED
        self.foods_eaten = 0
        self._tick_accumulator = 0.0

        # Toast messages
        self._toast_text: Optional[str] = None
        self._toast_timer: float = 0.0

        # Death animation
        self._death_timer: float = 0.0
        self._death_phase: int = 0

        # Menu selection index
        self._menu_idx = 0

    # ------------------------------------------------------------------
    # Main entry
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Blocking main loop -- returns when the user quits."""
        running = True
        while running:
            dt = self.clock.tick(CFG.FPS) / 1000.0
            running = self._handle_events()
            self._update(dt)
            self._draw()
        pygame.quit()

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.state == State.MENU:
                    self._handle_menu_input(event)
                elif self.state == State.PLAYING:
                    self._handle_playing_input(event)
                elif self.state == State.PAUSED:
                    self._handle_paused_input(event)
                elif self.state == State.GAME_OVER:
                    self._handle_gameover_input(event)
        return True

    def _handle_menu_input(self, event: pygame.event.Event) -> None:
        key = event.key
        if key in (pygame.K_UP, pygame.K_w):
            self._menu_idx = (self._menu_idx - 1) % 3
        elif key in (pygame.K_DOWN, pygame.K_s):
            self._menu_idx = (self._menu_idx + 1) % 3
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            # menu_idx: 0 = mode, 1 = start, 2 = quit
            if self._menu_idx == 0:
                self.game_mode = (
                    GameMode.WRAP_AROUND
                    if self.game_mode == GameMode.HARD_WALLS
                    else GameMode.HARD_WALLS
                )
            elif self._menu_idx == 1:
                self._start_game()
            elif self._menu_idx == 2:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _handle_playing_input(self, event: pygame.event.Event) -> None:
        key = event.key
        if key in (pygame.K_UP, pygame.K_w):
            self.snake.queue_direction("UP")
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.snake.queue_direction("DOWN")
        elif key in (pygame.K_LEFT, pygame.K_a):
            self.snake.queue_direction("LEFT")
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.snake.queue_direction("RIGHT")
        elif key == pygame.K_p:
            self.food.pause()
            self.state = State.PAUSED
        elif key == pygame.K_ESCAPE:
            if self.score > self.high_score:
                self.high_score = self.score
                self._save_high_score()
            self.state = State.MENU

    def _handle_paused_input(self, event: pygame.event.Event) -> None:
        if event.key in (pygame.K_p, pygame.K_RETURN, pygame.K_SPACE):
            self.food.unpause()
            self.state = State.PLAYING
        elif event.key == pygame.K_ESCAPE:
            if self.score > self.high_score:
                self.high_score = self.score
                self._save_high_score()
            self.state = State.MENU

    def _handle_gameover_input(self, event: pygame.event.Event) -> None:
        if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_r):
            self._start_game()
        elif event.key in (pygame.K_ESCAPE, pygame.K_q):
            self.state = State.MENU

    # ------------------------------------------------------------------
    # Update logic
    # ------------------------------------------------------------------

    def _update(self, dt: float) -> None:
        if self.state == State.PLAYING:
            self._tick_accumulator += dt
            interval = 1.0 / self.speed
            while self._tick_accumulator >= interval:
                self._tick_accumulator -= interval
                alive = self._game_tick()
                if not alive or self.state != State.PLAYING:
                    break

            # Tick toast timer (only while playing)
            if self._toast_timer > 0:
                self._toast_timer -= dt
                if self._toast_timer <= 0:
                    self._toast_text = None

            # Tick food manager (expire golden apples, ensure regular exists)
            self.food.tick(set(self.snake.body))

        # Death animation timer
        if self.state == State.GAME_OVER:
            self._death_timer += dt

    def _game_tick(self) -> bool:
        """Advance the snake one cell.  Returns False on death."""
        _pos, alive = self.snake.advance(wrap=(self.game_mode == GameMode.WRAP_AROUND))
        if not alive:
            self._on_death()
            return False

        eaten = self.food.on_food_eaten(self.snake.head, set(self.snake.body))
        if eaten is not None:
            self.snake.grow()
            points = eaten.points
            if self.game_mode == GameMode.WRAP_AROUND:
                points *= CFG.WRAP_SCORE_MULTIPLIER
            self.score += points
            self.foods_eaten += 1
            self._maybe_increase_speed()
            self._check_milestone(points)
        return True

    def _maybe_increase_speed(self) -> None:
        if self.foods_eaten % CFG.SPEED_FOOD_INTERVAL == 0:
            self.speed = min(
                self.speed + CFG.SPEED_INCREMENT, CFG.MAX_SPEED
            )

    def _check_milestone(self, points_earned: int) -> None:
        milestones = {5, 10, 15, 20, 25, 30, 40, 50, 75, 100}
        prev = self.score - points_earned
        for m in milestones:
            if prev < m <= self.score:
                self._show_toast(f"{m}!", 1.5)
                break

    def _show_toast(self, text: str, duration: float = 1.5) -> None:
        self._toast_text = text
        self._toast_timer = duration

    def _on_death(self) -> None:
        self.state = State.GAME_OVER
        self._death_timer = 0.0
        self._death_phase = 0
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score()

    def _start_game(self) -> None:
        self.snake.reset()
        self.food.reset(set(self.snake.body))
        self.food.unpause()
        self.score = 0
        self.foods_eaten = 0
        # Apply wrap-mode speed bonus
        self.speed = CFG.INITIAL_SPEED
        if self.game_mode == GameMode.WRAP_AROUND:
            self.speed *= CFG.WRAP_SPEED_MULTIPLIER
        self._tick_accumulator = 0.0
        self._toast_text = None
        self._toast_timer = 0.0
        self.state = State.PLAYING

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _draw(self) -> None:
        self.screen.fill(CFG.BG_COLOR)

        if self.state == State.MENU:
            self._draw_menu()
        elif self.state in (State.PLAYING, State.PAUSED):
            self._draw_game()
            if self.state == State.PAUSED:
                self._draw_pause_overlay()
        elif self.state == State.GAME_OVER:
            self._draw_game()
            self._draw_game_over()

        pygame.display.flip()

    # ---- grid helpers ------------------------------------------------

    def _cell_rect(self, gx: int, gy: int) -> pygame.Rect:
        return pygame.Rect(
            gx * CFG.GRID_SIZE,
            gy * CFG.GRID_SIZE,
            CFG.GRID_SIZE,
            CFG.GRID_SIZE,
        )

    # ---- game field --------------------------------------------------

    def _draw_game(self) -> None:
        # Border (only in hard-walls mode)
        if self.game_mode == GameMode.HARD_WALLS:
            bw = 3
            border_rect = pygame.Rect(
                bw // 2, bw // 2,
                self.cols * CFG.GRID_SIZE - bw, self.grid_pixel_h - bw,
            )
            pygame.draw.rect(self.screen, CFG.BORDER_COLOR, border_rect, bw)

        # Food
        for item in self.food.items:
            rect = self._cell_rect(*item.pos)
            color = CFG.GOLDEN_FOOD_COLOR if item.is_golden else CFG.FOOD_COLOR
            # Pulse golden food
            if item.is_golden:
                pulse = 0.7 + 0.3 * math.sin(time.monotonic() * 6)
                color = tuple(int(c * pulse) for c in color)
            inner = rect.inflate(-4, -4)
            pygame.draw.rect(self.screen, color, inner, border_radius=4)

        # Snake body (skip head)
        for i, seg in enumerate(self.snake.body):
            if i == 0:
                continue
            rect = self._cell_rect(*seg)
            inner = rect.inflate(-2, -2)
            color = CFG.SNAKE_BODY_COLOR if i % 2 == 0 else CFG.SNAKE_BODY_ALT
            pygame.draw.rect(self.screen, color, inner, border_radius=3)

        # Snake head
        if self.snake.body:
            rect = self._cell_rect(*self.snake.head)
            inner = rect.inflate(-2, -2)
            pygame.draw.rect(self.screen, CFG.SNAKE_HEAD_COLOR, inner, border_radius=5)
            # Eyes
            dx, dy = self.snake.direction.dx, self.snake.direction.dy
            cx, cy = rect.centerx, rect.centery
            eye_offset = 4
            if dx != 0:
                e1 = (cx + dx * 4, cy - eye_offset)
                e2 = (cx + dx * 4, cy + eye_offset)
            else:
                e1 = (cx - eye_offset, cy + dy * 4)
                e2 = (cx + eye_offset, cy + dy * 4)
            pygame.draw.circle(self.screen, (30, 30, 30), e1, 2)
            pygame.draw.circle(self.screen, (30, 30, 30), e2, 2)

        # HUD
        self._draw_hud()

        # Toast
        if self._toast_text:
            surf = self.font.render(self._toast_text, True, CFG.GOLDEN_FOOD_COLOR)
            rx = (self.cols * CFG.GRID_SIZE - surf.get_width()) // 2
            ry = (self.grid_pixel_h - surf.get_height()) // 2
            self.screen.blit(surf, (rx, ry))

    def _draw_hud(self) -> None:
        y = self.grid_pixel_h + 6
        score_surf = self.font.render(
            f"SCORE: {self.score}", True, CFG.ACCENT_COLOR
        )
        hi_surf = self.small_font.render(
            f"HIGH: {self.high_score}", True, CFG.DIM_TEXT_COLOR
        )
        len_surf = self.small_font.render(
            f"LEN: {self.snake.length}", True, CFG.DIM_TEXT_COLOR
        )
        mode_label = (
            f"WRAP x{CFG.WRAP_SCORE_MULTIPLIER}" if self.game_mode == GameMode.WRAP_AROUND else "WALLS"
        )
        mode_color = CFG.GOLDEN_FOOD_COLOR if self.game_mode == GameMode.WRAP_AROUND else CFG.DIM_TEXT_COLOR
        mode_surf = self.small_font.render(
            f"MODE: {mode_label}", True, mode_color
        )
        speed_surf = self.small_font.render(
            f"SPD: {self.speed:.1f}", True, CFG.DIM_TEXT_COLOR
        )
        pause_surf = self.small_font.render(
            "[P] Pause", True, CFG.DIM_TEXT_COLOR
        )

        self.screen.blit(score_surf, (8, y))
        self.screen.blit(hi_surf, (score_surf.get_width() + 20, y + 4))
        x_next = score_surf.get_width() + hi_surf.get_width() + 36
        self.screen.blit(len_surf, (x_next, y + 4))
        x_next += len_surf.get_width() + 16
        self.screen.blit(mode_surf, (x_next, y + 4))
        x_next += mode_surf.get_width() + 16
        self.screen.blit(speed_surf, (x_next, y + 4))
        x_next += speed_surf.get_width() + 16
        self.screen.blit(pause_surf, (x_next, y + 4))

    # ---- pause overlay -----------------------------------------------

    def _draw_pause_overlay(self) -> None:
        overlay = pygame.Surface(
            (self.cols * CFG.GRID_SIZE, self.grid_pixel_h),
            pygame.SRCALPHA,
        )
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        txt = self.title_font.render("PAUSED", True, CFG.ACCENT_COLOR)
        rx = (self.cols * CFG.GRID_SIZE - txt.get_width()) // 2
        ry = (self.grid_pixel_h - txt.get_height()) // 2
        self.screen.blit(txt, (rx, ry))

        sub = self.small_font.render(
            "P / Enter / Space to resume  |  ESC for menu", True, CFG.DIM_TEXT_COLOR
        )
        self.screen.blit(
            sub,
            (
                (self.cols * CFG.GRID_SIZE - sub.get_width()) // 2,
                ry + txt.get_height() + 12,
            ),
        )

    # ---- game over ---------------------------------------------------

    def _draw_game_over(self) -> None:
        gw = self.cols * CFG.GRID_SIZE
        gh = self.grid_pixel_h
        overlay = pygame.Surface((gw, gh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        # Flash the snake during death animation
        if self._death_timer < 1.0:
            phase = int(self._death_timer * 10) % 2
            if phase != self._death_phase:
                self._death_phase = phase
            for seg in self.snake.body:
                rect = self._cell_rect(*seg)
                inner = rect.inflate(-2, -2)
                c = CFG.DANGER_COLOR if phase == 0 else CFG.SNAKE_BODY_COLOR
                pygame.draw.rect(self.screen, c, inner, border_radius=3)
            # Redraw head on top
            rect = self._cell_rect(*self.snake.head)
            inner = rect.inflate(-2, -2)
            pygame.draw.rect(self.screen, CFG.DANGER_COLOR, inner, border_radius=5)

        # Game Over text
        is_new = self.score >= self.high_score and self.score > 0
        title = self.title_font.render("GAME OVER", True, CFG.DANGER_COLOR)
        title_x = (gw - title.get_width()) // 2
        title_y = gh // 2 - 60
        self.screen.blit(title, (title_x, title_y))

        score_txt = self.font.render(
            f"Score: {self.score}", True, CFG.TEXT_COLOR
        )
        self.screen.blit(
            score_txt,
            ((gw - score_txt.get_width()) // 2, title_y + 60),
        )

        if is_new:
            new_hi = self.font.render(
                "NEW HIGH SCORE!", True, CFG.GOLDEN_FOOD_COLOR
            )
            self.screen.blit(
                new_hi,
                ((gw - new_hi.get_width()) // 2, title_y + 96),
            )
        else:
            hi_txt = self.small_font.render(
                f"High Score: {self.high_score}", True, CFG.DIM_TEXT_COLOR
            )
            self.screen.blit(
                hi_txt,
                ((gw - hi_txt.get_width()) // 2, title_y + 96),
            )

        hint = self.small_font.render(
            "[R] Restart   [ESC] Menu", True, CFG.DIM_TEXT_COLOR
        )
        self.screen.blit(
            hint,
            ((gw - hint.get_width()) // 2, title_y + 136),
        )

    # ---- menu --------------------------------------------------------

    def _draw_menu(self) -> None:
        gw = self.cols * CFG.GRID_SIZE
        gh = self.grid_pixel_h

        # Title
        title = self.title_font.render("SNAKE", True, CFG.SNAKE_HEAD_COLOR)
        self.screen.blit(
            title, ((gw - title.get_width()) // 2, gh // 4)
        )

        # High score
        hi = self.small_font.render(
            f"High Score: {self.high_score}", True, CFG.DIM_TEXT_COLOR
        )
        self.screen.blit(
            hi, ((gw - hi.get_width()) // 2, gh // 4 + title.get_height() + 8)
        )

        # Menu items
        if self.game_mode == GameMode.WRAP_AROUND:
            mode_label = f"Mode: Wrap-Around  (x{CFG.WRAP_SCORE_MULTIPLIER} pts, {int(CFG.WRAP_SPEED_MULTIPLIER*100)}% spd)"
        else:
            mode_label = "Mode: Hard Walls"
        items = [mode_label, "Start Game", "Quit"]
        start_y = gh // 2 + 20
        for i, label in enumerate(items):
            color = CFG.ACCENT_COLOR if i == self._menu_idx else CFG.TEXT_COLOR
            prefix = "> " if i == self._menu_idx else "  "
            surf = self.font.render(f"{prefix}{label}", True, color)
            self.screen.blit(
                surf, ((gw - surf.get_width()) // 2, start_y + i * 40)
            )

        # Controls hint
        ctrl = self.small_font.render(
            "Arrow Keys / WASD to navigate  |  Enter to select",
            True,
            CFG.DIM_TEXT_COLOR,
        )
        self.screen.blit(
            ctrl, ((gw - ctrl.get_width()) // 2, gh - 60)
        )

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load_high_score(self) -> int:
        try:
            with open(CFG.HIGH_SCORE_FILE, "r") as fh:
                return int(fh.read().strip())
        except (FileNotFoundError, ValueError):
            return 0

    def _save_high_score(self) -> None:
        try:
            with open(CFG.HIGH_SCORE_FILE, "w") as fh:
                fh.write(str(self.high_score))
        except OSError:
            pass
