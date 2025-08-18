import numpy as np
class PriceEnv:
    def __init__(self, demand_fn, price_grid):
        self.demand_fn = demand_fn; self.price_grid = price_grid; self.state = 0
    def reset(self): self.state = 0; return self.state
    def step(self, action_idx):
        price = self.price_grid[action_idx]; demand = self.demand_fn(price)
        reward = price * demand; return self.state, reward, False, {}

class QLearningAgent:
    def __init__(self, n_actions, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.Q = np.zeros((1, n_actions)); self.alpha, self.gamma, self.epsilon = alpha, gamma, epsilon; self.n_actions = n_actions
    def select_action(self, state):
        import numpy as np
        if np.random.rand() < self.epsilon: return np.random.randint(self.n_actions)
        return int(np.argmax(self.Q[state]))
    def update(self, s, a, r, s_next):
        best_next = np.max(self.Q[s_next]); td = r + self.gamma * best_next - self.Q[s, a]; self.Q[s, a] += self.alpha * td

def simple_demand(price, a=150, b=5.0): return max(0.0, a - b * price)
