import os
import random
import sys
import time
import msvcrt

os.system("")

# ── ANSI Color & Style Codes ──────────────────────────────────────────
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

FG_BLACK = "\033[30m"
FG_RED = "\033[31m"
FG_GREEN = "\033[32m"
FG_YELLOW = "\033[33m"
FG_BLUE = "\033[34m"
FG_MAGENTA = "\033[35m"
FG_CYAN = "\033[36m"
FG_WHITE = "\033[37m"
FG_BRIGHT_RED = "\033[91m"
FG_BRIGHT_GREEN = "\033[92m"
FG_BRIGHT_YELLOW = "\033[93m"
FG_BRIGHT_BLUE = "\033[94m"
FG_BRIGHT_MAGENTA = "\033[95m"
FG_BRIGHT_CYAN = "\033[96m"
FG_BRIGHT_WHITE = "\033[97m"

# Theme palette
C_BORDER = FG_BRIGHT_YELLOW + BOLD
C_HEAD = FG_BRIGHT_GREEN + BOLD
C_SCORE = FG_BRIGHT_CYAN + BOLD
C_TITLE = FG_BRIGHT_YELLOW + BOLD
C_GAMEOVER = FG_BRIGHT_RED + BOLD
C_INSTR = FG_BRIGHT_WHITE

# Rainbow palette for snake body segments
RAINBOW = [
    FG_BRIGHT_RED, FG_BRIGHT_YELLOW, FG_BRIGHT_GREEN, FG_BRIGHT_CYAN,
    FG_BRIGHT_BLUE, FG_BRIGHT_MAGENTA,
]

# Score milestones for toast messages
MILESTONES = {5, 10, 15, 20, 25, 30, 40, 50, 75, 100}

FOOD_ITEMS = ["@", "♦", "♥", "★", "●", "◆", "▲", "♣", "⬟"]

HIGH_SCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".snake_highscore")


def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_high_score(score):
    try:
        with open(HIGH_SCORE_FILE, "w") as f:
            f.write(str(score))
    except OSError:
        pass


def clear_screen():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def get_terminal_size():
    try:
        cols, lines = os.get_terminal_size()
        width = (cols - 2) // 2 * 2
        height = lines - 4
    except OSError:
        width, height = 40, 20
    return max(width, 20), max(height, 10)


class SnakeGame:
    def __init__(self):
        self.width, self.height = get_terminal_size()
        self.snake = None
        self.direction = None
        self.next_direction = None
        self.food = None
        self.food_char = None
        self.score = 0
        self.high_score = load_high_score()
        self.speed = 0.12
        self.popup_pos = None
        self.popup_timer = 0
        self.toast_msg = None
        self.toast_timer = 0
        self.reached_milestones = set()
        self.reset()

    def reset(self):
        cy, cx = self.height // 2, self.width // 2
        self.snake = [[cy, cx], [cy, cx - 1], [cy, cx - 2]]
        self.direction = "RIGHT"
        self.next_direction = "RIGHT"
        self.score = 0
        self.speed = 0.12
        self.popup_pos = None
        self.popup_timer = 0
        self.toast_msg = None
        self.toast_timer = 0
        self.reached_milestones = set()
        self.spawn_food()

    def spawn_food(self):
        self.food_char = random.choice(FOOD_ITEMS)
        while True:
            pos = [
                random.randint(1, self.height - 2),
                random.randint(1, self.width - 2),
            ]
            if pos not in self.snake:
                self.food = pos
                return

    def draw_title(self):
        title = r"""
  ╔══════════════════════════════════════╗
  ║         ⚡  S N A K E  2.0  ⚡        ║
  ╚══════════════════════════════════════╝
"""
        sys.stdout.write(C_TITLE + title + RESET)

    def draw_instructions(self):
        lines = [
            f"{C_INSTR}  🡑 🡓 🡐 🡒  or  W A S D     Move",
            f"  {C_INSTR}P                    Pause",
            f"  {C_INSTR}R                    Restart",
            f"  {C_INSTR}Q or ESC             Quit{RESET}",
        ]
        sys.stdout.write("\n".join(lines))

    def show_start_screen(self):
        clear_screen()
        self.draw_title()
        sys.stdout.write("\n")
        self.draw_instructions()
        sys.stdout.write(f"\n\n{C_SCORE}  HIGH SCORE: {self.high_score}{RESET}")
        sys.stdout.write(f"\n\n{C_INSTR}  Press any key to start...{RESET}")
        sys.stdout.flush()
        msvcrt.getch()

    def show_countdown(self):
        for i in ("3", "2", "1", "GO!"):
            clear_screen()
            color = FG_BRIGHT_YELLOW if i != "GO!" else FG_BRIGHT_GREEN
            msg = f"{color}{BOLD}{i}{RESET}"
            cx = self.width // 2 - 1
            cy = self.height // 2
            sys.stdout.write(f"\033[{cy};{cx}H{msg}")
            sys.stdout.flush()
            time.sleep(0.6 if i != "GO!" else 0.4)

    def show_game_over_screen(self):
        clear_screen()
        if self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.high_score)
            new_record = True
        else:
            new_record = False

        game_over_art = f"""\
{C_GAMEOVER}█████████████████████████████████████████████████████████{RESET}
{C_GAMEOVER}██{RESET}                                                     {C_GAMEOVER}██{RESET}
{C_GAMEOVER}██{RESET}{FG_BRIGHT_WHITE} #####  ###  #   # #####      ###  #   # ##### ####  {RESET}{C_GAMEOVER}██{RESET}
{C_GAMEOVER}██{RESET}{FG_BRIGHT_WHITE} #     #   # ## ## #         #   # #   # #     #   # {RESET}{C_GAMEOVER}██{RESET}
{C_GAMEOVER}██{RESET}{FG_BRIGHT_WHITE} # ### ##### # # # ####      #   #  # #  ####  ####  {RESET}{C_GAMEOVER}██{RESET}
{C_GAMEOVER}██{RESET}{FG_BRIGHT_WHITE} #   # #   # #   # #         #   #  # #  #     #  #  {RESET}{C_GAMEOVER}██{RESET}
{C_GAMEOVER}██{RESET}{FG_BRIGHT_WHITE} ##### #   # #   # #####      ###    #   ##### #   # {RESET}{C_GAMEOVER}██{RESET}
{C_GAMEOVER}██{RESET}                                                     {C_GAMEOVER}██{RESET}
{C_GAMEOVER}█████████████████████████████████████████████████████████{RESET}"""
        sys.stdout.write(game_over_art)

        sys.stdout.write(f"\n{C_SCORE}╔════════════════════════════╗\n")
        sys.stdout.write(f"║     FINAL SCORE: {self.score:<5}    ║\n")
        sys.stdout.write(f"║     HIGH SCORE:  {self.high_score:<5}    ║\n")
        if new_record:
            sys.stdout.write(f"║  {FG_BRIGHT_YELLOW}★  NEW HIGH SCORE!  ★{C_SCORE}   ║\n")
        sys.stdout.write(f"╚════════════════════════════╝{RESET}\n")
        sys.stdout.write(f"\n{C_INSTR}  [R] Restart    [Q] Quit{RESET}")
        sys.stdout.flush()

        while True:
            key = msvcrt.getch()
            try:
                c = key.decode("utf-8").lower()
            except UnicodeDecodeError:
                c = ""
            if c == "r":
                self.reset()
                return True
            elif c == "q" or key == b"\x1b":
                return False
            if key in (b"\r", b" "):
                self.reset()
                return True

    def get_input(self):
        if not msvcrt.kbhit():
            return
        raw_key = msvcrt.getch()
        if raw_key in (b"\x00", b"\xe0"):
            arrow = msvcrt.getch()
            if arrow == b"H" and self.direction != "DOWN":
                self.next_direction = "UP"
            elif arrow == b"P" and self.direction != "UP":
                self.next_direction = "DOWN"
            elif arrow == b"K" and self.direction != "RIGHT":
                self.next_direction = "LEFT"
            elif arrow == b"M" and self.direction != "LEFT":
                self.next_direction = "RIGHT"
        else:
            try:
                c = raw_key.decode("utf-8").lower()
            except UnicodeDecodeError:
                return
            if c == "w" and self.direction != "DOWN":
                self.next_direction = "UP"
            elif c == "s" and self.direction != "UP":
                self.next_direction = "DOWN"
            elif c == "a" and self.direction != "RIGHT":
                self.next_direction = "LEFT"
            elif c == "d" and self.direction != "LEFT":
                self.next_direction = "RIGHT"
            elif c == "p":
                self.pause()
            elif c == "r":
                self.reset()
            elif c == "q" or raw_key == b"\x1b":
                self.show_game_over_screen()
                sys.exit(0)

    def pause(self):
        cx, cy = self.width // 2 - 5, self.height // 2
        pause_msg = "  ⏸ PAUSED  "
        sys.stdout.write(f"\033[{cy};{cx}H{C_TITLE}{pause_msg}{RESET}")
        sys.stdout.flush()
        while True:
            k = msvcrt.getch()
            try:
                c = k.decode("utf-8").lower()
            except UnicodeDecodeError:
                c = ""
            if c == "p":
                break
            if c == "q" or k == b"\x1b":
                self.show_game_over_screen()
                sys.exit(0)
            if c == "r":
                self.reset()
                return

    def update(self):
        self.direction = self.next_direction
        head = self.snake[0].copy()
        if self.direction == "UP":
            head[0] -= 1
        elif self.direction == "DOWN":
            head[0] += 1
        elif self.direction == "LEFT":
            head[1] -= 1
        elif self.direction == "RIGHT":
            head[1] += 1

        self.snake.insert(0, head)

        if (
            head[0] <= 0
            or head[0] >= self.height - 1
            or head[1] <= 0
            or head[1] >= self.width - 1
        ):
            return False
        if head in self.snake[1:]:
            return False

        if head == self.food:
            self.score += 1
            self.speed = max(0.05, self.speed - 0.002)
            self.popup_pos = self.food[:]
            self.popup_timer = 4
            if self.score in MILESTONES and self.score not in self.reached_milestones:
                self.reached_milestones.add(self.score)
                self.toast_msg = f"🔥 {self.score}!"
                self.toast_timer = 10
            self.spawn_food()
        else:
            self.snake.pop()

        if self.popup_timer > 0:
            self.popup_timer -= 1
            if self.popup_timer == 0:
                self.popup_pos = None
        if self.toast_timer > 0:
            self.toast_timer -= 1
            if self.toast_timer == 0:
                self.toast_msg = None

        return True

    def draw(self):
        sys.stdout.write("\033[H")
        border_color = C_BORDER
        rows = []

        pos_to_color = {}
        for i, seg in enumerate(self.snake):
            if i == 0:
                continue
            pos_to_color[(seg[0], seg[1])] = RAINBOW[(i - 1) % len(RAINBOW)]

        for y in range(self.height):
            row = ""
            skip = False
            for x in range(self.width):
                if skip:
                    skip = False
                    continue
                if y == 0 and x == 0:
                    row += f"{border_color}╔{RESET}"
                elif y == 0 and x == self.width - 1:
                    row += f"{border_color}╗{RESET}"
                elif y == self.height - 1 and x == 0:
                    row += f"{border_color}╚{RESET}"
                elif y == self.height - 1 and x == self.width - 1:
                    row += f"{border_color}╝{RESET}"
                elif y == 0 or y == self.height - 1:
                    row += f"{border_color}═{RESET}"
                elif x == 0 or x == self.width - 1:
                    row += f"{border_color}║{RESET}"
                elif [y, x] == self.snake[0]:
                    row += f"{C_HEAD}●{RESET}"
                elif (y, x) in pos_to_color:
                    row += f"{pos_to_color[(y, x)]}■{RESET}"
                elif [y, x] == self.food:
                    row += f"{self.food_char}"
                elif self.popup_pos and [y, x] == self.popup_pos:
                    row += f"{FG_BRIGHT_YELLOW}+1{RESET}"
                    skip = True
                else:
                    row += " "
            rows.append(row)

        score_bar = (
            f"{C_SCORE}  SCORE: {self.score:>4}"
            f"{RESET}  │  {DIM}HIGH: {self.high_score}{RESET}"
            f"  │  {DIM}LEN: {len(self.snake)}{RESET}"
        )
        sys.stdout.write("\n".join(rows))
        sys.stdout.write(f"\n\n{score_bar}\n")

        if self.toast_msg:
            tx = self.width // 2 - len(self.toast_msg) // 2
            ty = self.height // 2
            sys.stdout.write(f"\033[{ty};{tx}H{FG_BRIGHT_YELLOW}{BOLD}{self.toast_msg}{RESET}")

        sys.stdout.flush()

    def run(self):
        self.show_start_screen()
        self.show_countdown()
        clear_screen()
        while True:
            self.get_input()
            alive = self.update()
            self.draw()
            if not alive:
                if not self.show_game_over_screen():
                    break
                clear_screen()
            time.sleep(self.speed * (2 if self.direction in ("UP", "DOWN") else 1))


if __name__ == "__main__":
    try:
        game = SnakeGame()
        game.run()
    except KeyboardInterrupt:
        pass
    finally:
        clear_screen()
        sys.stdout.write(f"{FG_GREEN}Thanks for playing!{RESET}\n")
        sys.stdout.flush()
