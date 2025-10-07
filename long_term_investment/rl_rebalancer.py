"""
RL-based portfolio rebalancer for Sentio 2.0
"""
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, Any

class RLPortfolioRebalancer:
    def __init__(self, n_assets: int, state_dim: int = None, hidden_dim: int = 64):
        self.n_assets = n_assets
        self.state_dim = state_dim or n_assets * 2  # weights + returns
        self.model = nn.Sequential(
            nn.Linear(self.state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, n_assets),
            nn.Softmax(dim=-1)
        )
        self.optimizer = optim.Adam(self.model.parameters(), lr=1e-3)
        self.loss_fn = nn.MSELoss()

    def get_action(self, state: np.ndarray) -> np.ndarray:
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            action = self.model(state_tensor).numpy().flatten()
        return action / action.sum()

    def train(self, states: np.ndarray, targets: np.ndarray, epochs: int = 10):
        for _ in range(epochs):
            state_tensor = torch.FloatTensor(states)
            target_tensor = torch.FloatTensor(targets)
            pred = self.model(state_tensor)
            loss = self.loss_fn(pred, target_tensor)
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

    def rebalance(self, portfolio: Dict[str, float], market_state: Dict[str, Any]) -> Dict[str, float]:
        # Example state: concatenate weights and recent returns
        weights = np.array(list(portfolio.values()))
        returns = np.array(market_state.get('returns', np.zeros(self.n_assets)))
        state = np.concatenate([weights, returns])
        action = self.get_action(state)
        total_value = sum(portfolio.values())
        rebalanced = {f'Asset_{i}': float(total_value * action[i]) for i in range(self.n_assets)}
        return rebalanced
