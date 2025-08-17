import random
from typing import Tuple, Any


class Food:
    def __init__(self, game: Any) -> None:
        self.game = game
        self.position: Tuple[int, int] = (
            random.randint(0, game.grid_width - 1),
            random.randint(0, game.grid_height - 1),
        )
        self.eaten: bool = False

    def spawn_food(self) -> None:
        if self.eaten:
            invalid_positions = self.game.snake.body + [self.position]
            valid_positions = [
                (x, y)
                for x in range(self.game.grid_width)
                for y in range(self.game.grid_height)
                if (x, y) not in invalid_positions
            ]
            if not valid_positions:
                self.game.game_over()
            self.position = random.choice(valid_positions)
            self.eaten = False

    def check_eaten(self) -> None:
        if self.position == self.game.snake.head:
            self.eaten = True
            self.game.score += 1
            self.game.snake.grow_snake()
            self.spawn_food()

    def to_dict(self) -> Tuple[int, int]:
        return self.position
