from typing import Deque, Tuple, List, Optional
import torch
import torch.nn as nn
from collections import deque
import random
from game import Game
from model import LinearQNet, QTrainer

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


class DQN(nn.Module):
    def __init__(self: "DQN") -> None:
        super().__init__()  # type: ignore
        self.n_games = 0
        self.avg_score: float = 0
        self.epsilon = 0.9
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.1
        self.gamma = 0.95
        self.memory: Deque[Tuple[torch.Tensor, List[int], int, torch.Tensor, bool]] = (
            deque(maxlen=MAX_MEMORY)
        )
        self.model: LinearQNet = LinearQNet(13, 256, 3)
        self.trainer: QTrainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game: "Game") -> torch.Tensor:
        head = game.snake.head

        def normalize_distance(dist: float, max_dist: float) -> float:
            return dist / max_dist

        def get_direction_state() -> list[int]:
            dir_state: list[int] = [0, 0, 0, 0]
            if game.snake.direction == (0, -1):
                dir_state[0] = 1
            elif game.snake.direction == (0, 1):
                dir_state[1] = 1
            elif game.snake.direction == (-1, 0):
                dir_state[2] = 1
            elif game.snake.direction == (1, 0):
                dir_state[3] = 1
            return dir_state

        def get_danger_state() -> list[bool]:
            danger_straight = False
            danger_right = False
            danger_left = False

            dir_up = game.snake.direction == (0, -1)
            dir_down = game.snake.direction == (0, 1)
            dir_left = game.snake.direction == (-1, 0)
            dir_right = game.snake.direction == (1, 0)

            def will_collide(point: tuple[int, int]) -> bool:
                x, y = point
                return (
                    x < 0
                    or x >= game.grid_width
                    or y < 0
                    or y >= game.grid_height
                    or point in game.snake.body
                )

            if (
                dir_up
                and will_collide((head[0], head[1] - 1))
                or dir_down
                and will_collide((head[0], head[1] + 1))
                or dir_left
                and will_collide((head[0] - 1, head[1]))
                or dir_right
                and will_collide((head[0] + 1, head[1]))
            ):
                danger_straight = True

            if (
                dir_up
                and will_collide((head[0] + 1, head[1]))
                or dir_down
                and will_collide((head[0] - 1, head[1]))
                or dir_left
                and will_collide((head[0], head[1] - 1))
                or dir_right
                and will_collide((head[0], head[1] + 1))
            ):
                danger_right = True

            if (
                dir_up
                and will_collide((head[0] - 1, head[1]))
                or dir_down
                and will_collide((head[0] + 1, head[1]))
                or dir_left
                and will_collide((head[0], head[1] + 1))
                or dir_right
                and will_collide((head[0], head[1] - 1))
            ):
                danger_left = True

            return [danger_straight, danger_right, danger_left]

        food_dir: list[int] = [0, 0, 0, 0]
        if game.food.position[1] < head[1]:
            food_dir[0] = 1
        if game.food.position[1] > head[1]:
            food_dir[1] = 1
        if game.food.position[0] < head[0]:
            food_dir[2] = 1
        if game.food.position[0] > head[0]:
            food_dir[3] = 1

        food_dist_x: float = normalize_distance(
            abs(game.food.position[0] - head[0]), game.grid_width
        )
        food_dist_y: float = normalize_distance(
            abs(game.food.position[1] - head[1]), game.grid_height
        )

        danger_state: list[bool] = get_danger_state()
        dir_state: list[int] = get_direction_state()

        state: list[float] = (
            danger_state + food_dir + [food_dist_x, food_dist_y] + dir_state
        )

        return torch.tensor(state, dtype=torch.float)

    from typing import Optional

    def calculate_reward(self, game: "Game", done: bool) -> int:
        reward = 0

        head = game.snake.head
        food = game.food.position
        prev_distance: Optional[int] = (
            self.previous_distance if hasattr(self, "previous_distance") else None
        )
        current_distance: int = abs(head[0] - food[0]) + abs(head[1] - food[1])

        if prev_distance is not None:
            if current_distance < prev_distance:
                reward += 1
            elif current_distance > prev_distance:
                reward -= 1

        self.previous_distance = current_distance

        if game.snake.grow:
            reward += 10

        if done:
            reward -= 10

        return reward

    def remember(
        self,
        state: torch.Tensor,
        action: list[int],
        reward: int,
        next_state: torch.Tensor,
        done: bool,
    ) -> None:
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self) -> None:
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(
        self,
        state: torch.Tensor,
        action: list[int],
        reward: int,
        next_state: torch.Tensor,
        done: bool,
    ) -> None:
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state: torch.Tensor) -> list[int]:
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        final_move: list[int] = [0] * 3

        if random.random() < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state = torch.tensor(state, dtype=torch.float).unsqueeze(0)
            with torch.no_grad():
                prediction = self.model(state)
                move = int(torch.argmax(prediction).item())
                final_move[move] = 1

        return final_move
