import numpy as np
import random
import json


class ReinforcementLearningAgent:
    def __init__(
        self,
        state_size,
        action_size,
        learning_rate=0.1,
        discount_factor=0.95,
        exploration_rate=1.0,
        exploration_decay=0.995,
        exploration_min=0.01,
    ):
        self.state_size = state_size
        self.action_size = action_size
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = exploration_rate
        self.epsilon_decay = exploration_decay
        self.epsilon_min = exploration_min
        self.q_table = {}

    def _get_state_key(self, state):
        return tuple(round(s, 4) for s in state)

    def choose_action(self, state):
        state_key = self._get_state_key(state)
        if np.random.rand() < self.epsilon or state_key not in self.q_table:
            return random.randint(0, self.action_size - 1)
        q_values = self.q_table.get(state_key, [0] * self.action_size)
        return int(np.argmax(q_values))

    def update_q_value(self, state, action, reward, next_state):
        state_key = self._get_state_key(state)
        next_state_key = self._get_state_key(next_state)

        q_values = self.q_table.get(state_key, [0] * self.action_size)
        next_q_values = self.q_table.get(next_state_key, [0] * self.action_size)

        q_values[action] = q_values[action] + self.lr * (
            reward + self.gamma * max(next_q_values) - q_values[action]
        )

        self.q_table[state_key] = q_values

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save_q_table(self, filename):
        serializable_q = {str(k): v for k, v in self.q_table.items()}
        with open(filename, 'w') as f:
            json.dump(serializable_q, f)

    def load_q_table(self, filename):
        with open(filename, 'r') as f:
            serializable_q = json.load(f)
        self.q_table = {eval(k): v for k, v in serializable_q.items()}
