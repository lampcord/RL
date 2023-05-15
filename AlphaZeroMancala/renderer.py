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

    @abstractmethod
    def get_move(self, legal_moves):
        raise NotImplementedError("get_move")
