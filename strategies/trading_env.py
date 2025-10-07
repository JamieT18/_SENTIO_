"""
Custom OpenAI Gym-compatible trading environment for Sentio RL agents
"""
import gym
import numpy as np
from datetime import datetime

class SentioTradingEnv(gym.Env):
    def __init__(self, market_data, initial_balance=10000, assets=None, regime: str = None, external_context: dict = None):
        super().__init__()
        self.market_data = market_data
        self.initial_balance = initial_balance
        self.current_step = 0
        self.balance = initial_balance
        self.assets = assets or ['open', 'high', 'low', 'close']
        self.action_space = gym.spaces.Discrete(2)  # 0: sell, 1: buy
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, shape=(len(self.assets),), dtype=np.float32)
        self.regime = regime
        self.external_context = external_context
        self.diagnostics = {}

    def reset(self):
        self.current_step = 0
        self.balance = self.initial_balance
        self.diagnostics = {'reset_time': datetime.now().isoformat(), 'regime': self.regime, 'external_context': self.external_context}
        return self._get_obs()

    def step(self, action):
        obs = self._get_obs()
        reward = 0
        done = self.current_step >= len(self.market_data) - 1
        info = {'regime': self.regime, 'external_context': self.external_context}
        row = self.market_data[self.current_step]
        if action == 1:  # buy
            reward = row['close'] - row['open']
        elif action == 0:  # sell
            reward = row['open'] - row['close']
        self.balance += reward
        self.current_step += 1
        self.diagnostics = {'step_time': datetime.now().isoformat(), 'action': action, 'reward': reward, 'regime': self.regime, 'external_context': self.external_context}
        return self._get_obs(), reward, done, info

    def _get_obs(self):
        row = self.market_data[self.current_step]
        obs = np.array([row[a] for a in self.assets], dtype=np.float32)
        # Optionally add regime/external context to observation (for advanced RL)
        if self.regime:
            obs = np.append(obs, hash(self.regime) % 1000)
        if self.external_context:
            obs = np.append(obs, sum(hash(str(v)) for v in self.external_context.values()) % 1000)
        return obs
