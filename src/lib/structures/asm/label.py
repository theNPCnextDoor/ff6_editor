import logging

from src.lib.structures import Bytes


class Label:
    _list = []

    def __init__(
        self,
        name: str,
        filename: str = None,
        position: Bytes = None,
        fixed_position: bool = False,
    ):
        logging.info(f'Creating label "{name}" with position {position.to_address()}')
        self.position = position
        self.name = name
        self.filename = filename
        self.fixed_position = fixed_position
        self._list.append(self)

    def __str__(self):
        return f"{self.name}"

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        return self.position < other.position

    def __hash__(self):
        return hash(self.position)

    @property
    def relative_address(self):
        return int(Bytes(value=self.position % 0x010000, length=2, endianness="little"))

    @classmethod
    def get_from_name(cls, name: str, filename: str):
        candidates = [label for label in cls._list if label.name == name and label.filename == filename]
        if not len(candidates):
            return None
        elif len(candidates) > 1:
            raise Warning("More than one candidate is returned.")
        return candidates[0]
