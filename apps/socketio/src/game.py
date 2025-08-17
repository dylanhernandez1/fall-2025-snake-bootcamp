from snake import Snake
from food import Food
import time

# import json
from typing import List, Dict, Any


class Game:
    def __init__(self) -> None:
        self.grid_width: int = 29
        self.grid_height: int = 19
        self.score: int = 0
        self.snake: Snake = Snake(self)
        self.food: Food = Food(self)
        self.running: bool = True
        self.game_tick: float = 0.03
        self.last_tick: float = time.time()
        self.change_queue: List[Any] = []

    def game_over(self) -> None:
        self.running = False

    def send(self) -> Dict[str, Any]:
        event: Dict[str, Any] = {
            "score": self.score,
            "tick": self.game_tick,
            "snake": self.snake.body,
            "food": self.food.position,
            "running": self.running,
        }
        return event

    def step(self) -> None:
        if not self.running:
            return
        if len(self.change_queue) > 0:
            self.snake.change_direction(self.change_queue.pop())
            self.change_queue = []
        self.snake.move()
        self.food.check_eaten()
        self.last_tick = time.time()

    def queue_change(self, update: Any) -> None:
        if not self.running:
            return
        self.change_queue.append(update)

    def reset(self) -> None:
        self.score = 0
        self.snake = Snake(self)
        self.food = Food(self)
        self.running = True
        self.last_tick = time.time()

    def to_vector(self) -> List[int]:
        return [
            self.snake.head[0],
            self.snake.head[1],
            self.food.position[0],
            self.food.position[1],
            self.snake.direction[0],
            self.snake.direction[1],
        ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grid_width": self.grid_width,
            "grid_height": self.grid_height,
            "game_tick": self.game_tick,
            "snake": self.snake.to_dict(),
            "food": self.food.to_dict(),
            "score": self.score,
        }
