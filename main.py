"""Entry point for the Snake game.

Usage::

    python main.py

"""

from game_engine import GameEngine


def main() -> None:
    engine = GameEngine()
    engine.run()


if __name__ == "__main__":
    main()
