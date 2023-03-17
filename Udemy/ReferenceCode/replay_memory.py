import numpy as np
import torch as T

class ReplayBuffer():
    def __init__(self, max_size, input_shape, n_actions, device):
        self.mem_size = max_size
        self.mem_cntr = 0
        self.device = device
        self.state_memory = T.tensor(np.zeros((self.mem_size, *input_shape), dtype=np.float32)).to(device)
        self.new_state_memory = T.tensor(np.zeros((self.mem_size, *input_shape), dtype=np.float32)).to(device)
        self.action_memory = T.tensor(np.zeros(self.mem_size, dtype=np.int64)).to(device)
        self.reward_memory = T.tensor(np.zeros(self.mem_size, dtype=np.float32)).to(device)
        self.terminal_memory = T.tensor(np.zeros(self.mem_size, dtype=np.bool_)).to(device)

    def store_transition(self, state, action, reward, state_, done):
        index = self.mem_cntr % self.mem_size
        self.state_memory[index] = T.tensor(state).to(self.device)
        self.new_state_memory[index] = T.tensor(state_).to(self.device)
        self.action_memory[index] = T.tensor(action).to(self.device)
        self.reward_memory[index] = T.tensor(reward).to(self.device)
        self.terminal_memory[index] = T.tensor(done).to(self.device)
        self.mem_cntr += 1

    def sample_buffer(self, batch_size):
        max_mem = min(self.mem_cntr, self.mem_size)
        batch = np.random.choice(max_mem, batch_size, replace=False)

        states = self.state_memory[batch]
        actions = self.action_memory[batch]
        rewards = self.reward_memory[batch]
        states_ = self.new_state_memory[batch]
        terminal = self.terminal_memory[batch]

        return states, actions, rewards, states_, terminal
