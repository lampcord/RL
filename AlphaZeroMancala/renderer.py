from abc import ABC, abstractmethod
"""
Renderer is used to render the board.

Interface:
render(state, turn, moves, info)


"""


class Renderer(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def render(self, state, turn, info):
        raise NotImplementedError("render")
