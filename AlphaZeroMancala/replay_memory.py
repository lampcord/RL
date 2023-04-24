import msgpack
import os


class ReplayMemory:
    def __init__(self, filename=None):
        self.memory = {}
        self.filename = filename
        self.read()

    def update(self, binary_state, turn, visits, wins):
        key = binary_state * 2 + turn.value
        value = (visits, wins)
        self.memory[key] = value

    def get(self, binary_state, turn):
        key = binary_state * 2 + turn.value
        return self.memory.get(key, (0.0, 0.0))

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

