from re import Match
from typing import Self
from src.lib.structures.bytes import Bytes, BytesType, Position, Endian
from src.lib.structures.asm.label import Label

from src.lib.structures.asm.script_line import ScriptLine, BankMixin, ImpossibleDestination, DestinationMixin


class Pointer(ScriptLine, BankMixin, DestinationMixin):
    def __init__(
        self,
        position: Position = None,
        destination: Position = None,
        data: Bytes = None
    ):
        if destination is None and data is None:
            raise ValueError("Either provide the destination or the data.")

        super().__init__(position=position)

        if destination and self.position.bank() != destination.bank():
            raise ImpossibleDestination(
                f"Destination '{destination.to_snes_address()}' can't be reached with pointer"
                f" at position '{position.to_snes_address()}'")

        self.destination = destination if destination is not None else self._data_to_destination(data=data)
        self.data = data if data is not None else self._destination_to_data(destination=destination)

    @classmethod
    def from_regex_match(cls, match: Match, position: Position, labels: list[Label]) -> Self:
        data, destination = None, None

        if label_name := match.group("label"):
            destination = cls.find_destination(label_name, labels)
        else:
            data = Bytes(value=match.group("number"), length=2, in_endian=Endian.LITTLE, out_endian=Endian.LITTLE)

        return cls(
            position=position,
            destination=destination,
            data=data
        )

    @classmethod
    def from_bytes(cls, value: bytes, position: BytesType = None) -> Self:
        return Pointer(position=position, data=Bytes(value))
    
    def to_line(self, show_address: bool = False, labels: list[Label] | None = None) -> str:
        output = "  ptr "
        label = None

        if labels:
            label = self.find_label(destination=self.destination, labels=labels)

        output += f"{label.name}" if label else f"${self.data}"
        output += f" # {self.position.to_snes_address()}" if show_address else ""

        return output

    @classmethod
    def _is_possible_destination(cls, position: Position, destination: Position):
        return position.bank() == destination.bank()

    def __bytes__(self) -> bytes:
        return bytes(self.data)

    def __eq__(self, other: Self) -> bool:
        return self.position == other.position and self.destination == other.destination

    def __str__(self) -> str:
        return f"ptr ${self.data}"


    def __repr__(self) -> str:
        return f"{self.position}: {str(self)}"

    def __len__(self):
        return 2

    def _data_to_destination(self, data: Bytes) -> Position:
        return Position(
            value=int(data) + self.position.bank(),
        )

    @staticmethod
    def _destination_to_data(destination: Position) -> Bytes:
        return Bytes(
            value=destination,
            out_endian=Endian.LITTLE,
            length=2
        )