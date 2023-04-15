import msgpack
import os
class MoveCache:
    def __init__(self, base_filename):
        self.filename = base_filename + ".csh"
        self.read()
        self.data = {}

    def read(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'rb') as f:
                packed_data = f.read()
                self.data = msgpack.unpackb(packed_data, strict_map_key=False)

    def get(self, key):
        if len(self.data) == 0:
            self.read()
        return self.data.get(key, None)

    def write(self):
        packed_data = msgpack.packb(self.data)
        with open(self.filename, 'wb') as f:
            f.write(packed_data)

    def set(self, key, value):
        self.data[key] = value
        self.write()


if __name__ == "__main__":
    mc = MoveCache('test_move_cache')

    for x in range(100):
        data = mc.get(x)
        if data is None:
            data = (2 * x, 3 * x)
            mc.set(x, data)
        print(x, data)

    for x in range(150):
        data = mc.get(x)
        if data is None:
            data = (3 * x, 4 * x)
            mc.set(x, data)
        print(x, data)