import logging

from src.lib.structures.fields import Bytes


class Label:
    def __init__(self, name: str, position: Bytes = None, fixed_position: bool = False):
        logging.info(f'Creating label "{name}" with position {position.to_address()}')
        self.position = position
        self.name = name
        self.fixed_position = fixed_position

    def __str__(self):
        return f"{self.name}"

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        return self.position < other.position

    def __hash__(self):
        return hash(self.position)
