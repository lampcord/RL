import msgpack
import os


class ReplayMemory:
    def __init__(self, filename=None):
        self.memory = {}
        self.filename = filename
        self.read()
        self.memory_found = 0.0
        self.memory_checks = 0.0

    def update(self, binary_state, visits, wins):
        current_visits, current_wins = self.memory.get(binary_state, (0, 0))
        value = (visits + current_visits, wins + current_wins)
        self.memory[binary_state] = value

    def get(self, binary_state):
        result = self.memory.get(binary_state, None)
        self.memory_checks += 1
        if result:
            self.memory_found += 1
        else:
            result = (0, 0)
        return result

    def read(self):
        if self.filename is None:
            return
        if os.path.exists(self.filename):
            with open(self.filename, 'rb') as f:
                packed_data = f.read()
                self.memory = msgpack.unpackb(packed_data, strict_map_key=False)

    def write(self):
        if self.filename is None:
            return
        packed_data = msgpack.packb(self.memory)
        with open(self.filename, 'wb') as f:
            f.write(packed_data)

    def scale(self, target=100.0):
        max_value = max(self.memory.values())[0]
        factor = target / max_value
        self.memory = {key: (visits * factor, wins * factor) for key, (visits, wins) in self.memory.items()}
        # for key, (visits, wins) in self.memory.items():
        #     print(key, visits, wins)
        # print(max(self.memory.values()))

