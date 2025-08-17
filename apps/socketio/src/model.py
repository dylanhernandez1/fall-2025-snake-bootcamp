import torch
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as F
import os
import datetime
from typing import Any


class LinearQNet(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, output_size: int) -> None:
        super().__init__()  # type: ignore
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x

    def save(self) -> None:
        model_folder_path = "./model"
        file_name = f'model-{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.pth'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)

    def load(self, file_name: str) -> None:
        file_name = os.path.join("./model", file_name)
        self.load_state_dict(torch.load(file_name))


class QTrainer:
    def __init__(self, model: nn.Module, lr: float, gamma: float) -> None:
        self.lr: float = lr
        self.gamma: float = gamma
        self.model: nn.Module = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(
        self, state: Any, action: Any, reward: Any, next_state: Any, done: Any
    ) -> None:
        if isinstance(state, tuple):
            state = torch.stack([s for s in state])  # type: ignore
            next_state = torch.stack([s for s in next_state])
            action = torch.tensor(action, dtype=torch.float)
            reward = torch.tensor(reward, dtype=torch.float)
        else:
            state = state.unsqueeze(0)
            next_state = next_state.unsqueeze(0)
            action = torch.tensor([action], dtype=torch.float)
            reward = torch.tensor([reward], dtype=torch.float)
            done = (done,)

        pred = self.model(state)
        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(  # type: ignore
                    self.model(next_state[idx].unsqueeze(0)).detach()
                )
            target[idx][torch.argmax(action[idx]).item()] = Q_new

        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        self.optimizer.step()  # type: ignore
