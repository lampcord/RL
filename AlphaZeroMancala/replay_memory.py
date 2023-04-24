

class ReplayMemory:
    def __init__(self):
        self.memory = {}

    def update(self, binary_state, turn, visits, wins):
        key = binary_state * 2 + turn.value
        value = (visits, wins)
        self.memory[key] = value

    def get(self, binary_state, turn):
        key = binary_state * 2 + turn.value
        return self.memory.get(key, (0.0, 0.0))