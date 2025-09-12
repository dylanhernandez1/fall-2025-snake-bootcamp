import random
from typing import Tuple, List, Any


class Snake:
    def __init__(self, game: Any) -> None:
        self.game = game
        self.body: List[Tuple[int, int]] = [
            (
                random.randint(game.grid_width // 2 - 5, game.grid_width // 2 + 5),
                random.randint(game.grid_height // 2 - 5, game.grid_height // 2 + 5),
            )
        ]
        self.head: Tuple[int, int] = self.body[0]
        self.direction: Tuple[int, int] = (0, 1)
        self.grow: bool = False

    def move(self) -> None:
        x, y = self.head
        dx, dy = self.direction
        new_head: Tuple[int, int] = (x + dx, y + dy)
        if new_head in self.body or not (
            0 <= new_head[0] < self.game.grid_width
            and 0 <= new_head[1] < self.game.grid_height
        ):
            self.game.game_over()
            return
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
        self.head = new_head

    def grow_snake(self) -> None:
        self.grow = True

    def change_direction(self, direction: str) -> None:
        if direction == "UP":
            self.direction = (0, -1)
        elif direction == "DOWN":
            self.direction = (0, 1)
        elif direction == "LEFT":
            self.direction = (-1, 0)
        elif direction == "RIGHT":
            self.direction = (1, 0)

    def to_dict(self) -> List[Tuple[int, int]]:
        return self.body
