from typing import Deque, Tuple, List, Optional
import torch
import torch.nn as nn
from collections import deque
import random
import numpy as np
from game import Game
from model import LinearQNet, QTrainer


# Define constants for the DQN agent
MAX_MEMORY = 100_000  # Maximum number of experiences to store
BATCH_SIZE = 1000  # Number of experiences to sample for training
LR = 0.001  # Learning rate for the neural network
GAMMA = 0.9  # Discount factor for future rewards
EPSILON_START = 80  # Starting exploration rate (80% random actions)
EPSILON_MIN = 0  # Minimum exploration rate
EPSILON_DECAY = 80  # How quickly epsilon decays


class DQN:
    """
    Deep Q-Network agent for playing Snake using reinforcement learning.

    This agent uses a neural network to learn the optimal policy for playing Snake.
    It learns through trial and error, getting rewards for good actions (eating food)
    and penalties for bad actions (hitting walls or itself).
    """

    def __init__(self) -> None:
        """Initialize the DQN agent with all necessary components."""
        # Training statistics
        self.n_games = 0
        self.total_score = 0
        self.record = 0
        
        # Epsilon-greedy exploration parameters
        self.epsilon = EPSILON_START
        
        # Memory for experience replay (stores transitions)
        self.memory: Deque[Tuple] = deque(maxlen=MAX_MEMORY)
        
        # Neural network: 13 inputs -> 256 hidden -> 3 outputs
        # 13 inputs: danger signals (3), current direction (4), food direction (4), distances (2)
        # 3 outputs: Q-values for [straight, right, left]
        self.model = LinearQNet(13, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=GAMMA)
        
        # Store previous distance for reward calculation
        self.prev_distance = None
        self.prev_length = 1

    def get_state(self, game: Game) -> List[float]:
        """
        Extract the current state of the game as input features for the neural network.

        The state includes:
        - Danger detection in three directions (straight, right, left)
        - Food direction relative to snake head (up, down, left, right)
        - Normalized distances to food
        - Current snake direction
        """
        head = game.snake.head
        point_l = (head[0] - 1, head[1])
        point_r = (head[0] + 1, head[1])
        point_u = (head[0], head[1] - 1)
        point_d = (head[0], head[1] + 1)
        
        dir_l = game.snake.direction == (-1, 0)
        dir_r = game.snake.direction == (1, 0)
        dir_u = game.snake.direction == (0, -1)
        dir_d = game.snake.direction == (0, 1)
        
        # Helper function to check if a point is dangerous
        def is_collision(pt: Tuple[int, int]) -> bool:
            # Hit boundary
            if pt[0] < 0 or pt[0] >= game.grid_width or pt[1] < 0 or pt[1] >= game.grid_height:
                return True
            # Hit itself
            if pt in game.snake.body[1:]:
                return True
            return False
        
        # Danger detection (straight, right, left relative to current direction)
        danger_straight = (
            (dir_r and is_collision(point_r)) or
            (dir_l and is_collision(point_l)) or
            (dir_u and is_collision(point_u)) or
            (dir_d and is_collision(point_d))
        )
        
        danger_right = (
            (dir_u and is_collision(point_r)) or
            (dir_d and is_collision(point_l)) or
            (dir_l and is_collision(point_u)) or
            (dir_r and is_collision(point_d))
        )
        
        danger_left = (
            (dir_d and is_collision(point_r)) or
            (dir_u and is_collision(point_l)) or
            (dir_r and is_collision(point_u)) or
            (dir_l and is_collision(point_d))
        )
        
        # Current direction as one-hot encoding
        dir_vec = [dir_l, dir_r, dir_u, dir_d]
        
        # Food direction relative to head
        food = game.food.position
        food_left = food[0] < head[0]
        food_right = food[0] > head[0]
        food_up = food[1] < head[1]
        food_down = food[1] > head[1]
        
        # Normalized distances to food
        dx = (food[0] - head[0]) / game.grid_width
        dy = (food[1] - head[1]) / game.grid_height
        
        # Combine all features into state vector
        state = [
            # Danger signals (3 features)
            int(danger_straight),
            int(danger_right),
            int(danger_left),
            
            # Current direction (4 features)
            int(dir_l),
            int(dir_r),
            int(dir_u),
            int(dir_d),
            
            # Food direction (4 features)
            int(food_left),
            int(food_right),
            int(food_up),
            int(food_down),
            
            # Normalized distances (2 features)
            dx,
            dy
        ]
        
        return state

    def calculate_reward(self, game: Game, done: bool) -> int:
        """
        Calculate the reward for the current game state.

        Rewards encourage good behavior:
        - Positive reward for eating food
        - Small positive reward for moving closer to food
        - Small negative reward for moving away from food
        - Large negative reward for dying
        """
        reward = 0
        
        # Get current positions
        head = game.snake.head
        food = game.food.position
        
        # Calculate current distance to food (Manhattan distance)
        current_distance = abs(head[0] - food[0]) + abs(head[1] - food[1])
        
        # Distance-based rewards (encourage moving toward food)
        if self.prev_distance is not None:
            if current_distance < self.prev_distance:
                reward += 1  # Moving closer to food
            elif current_distance > self.prev_distance:
                reward -= 1.5  # Moving away from food
        
        self.prev_distance = current_distance
        
        # Big reward for eating food
        if len(game.snake.body) > self.prev_length:
            reward += 10
            self.prev_distance = None  # Reset for new food
        
        # Store current length for next comparison
        self.prev_length = len(game.snake.body)
        
        # Big penalty for dying
        if done:
            reward -= 10
            self.prev_distance = None
        
        return reward

    def remember(
        self,
        state: List[float],
        action: List[int],
        reward: int,
        next_state: List[float],
        done: bool,
    ) -> None:
        """Store an experience in memory for later training (experience replay)."""
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self) -> None:
        """Train the neural network on a batch of experiences from memory."""
        if len(self.memory) > BATCH_SIZE:
            # Sample a random batch from memory
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            # Use all available memory if less than batch size
            mini_sample = self.memory
        
        # Unpack the batch
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        
        # Train the model on the batch
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(
        self,
        state: List[float],
        action: List[int],
        reward: int,
        next_state: List[float],
        done: bool,
    ) -> None:
        """Train the neural network on a single experience (immediate learning)."""
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state: List[float]) -> List[int]:
        """
        Choose an action based on the current state.

        Uses epsilon-greedy strategy:
        - With probability epsilon: choose random action (exploration)
        - With probability 1-epsilon: choose best action from neural network (exploitation)

        Actions: [1,0,0] = straight, [0,1,0] = turn right, [0,0,1] = turn left
        """
        # Decay epsilon over time (explore less as agent learns)
        self.epsilon = EPSILON_START - self.n_games
        if self.epsilon < EPSILON_MIN:
            self.epsilon = EPSILON_MIN
        
        # Initialize action array
        final_move = [0, 0, 0]
        
        # Epsilon-greedy action selection
        if random.randint(0, 200) < self.epsilon:
            # Random action (exploration)
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            # Best action from neural network (exploitation)
            state_tensor = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state_tensor)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        
        return final_move