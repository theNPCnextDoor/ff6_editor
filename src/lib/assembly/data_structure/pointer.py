from re import Match
from typing import Self

from src.lib.assembly.data_structure.regex import ToLineMixin
from src.lib.assembly.bytes import Bytes
from src.lib.assembly.artifact.variable import Label

from src.lib.assembly.data_structure.data_structure import DataStructure, BankMixin, DestinationMixin
from src.lib.misc.exception import ImpossibleDestination


class Pointer(DataStructure, BankMixin, DestinationMixin, ToLineMixin):
    """
    Pointers are used in the script to point to an element in a list containing elements of varying sizes. Pointers can
     either be direct, where they can point to anywhere in the same bank at the pointer itself. Or they can be relative,
     where they can point to anywhere from an anchor to the end of said anchor's bank.
    """

    def __init__(
        self,
        position: Bytes | None = None,
        destination: Bytes | None = None,
        data: Bytes | None = None,
        anchor: Bytes | None = None,
    ):
        """
        :param position: The position of the pointer.
        :param destination: The destination of the pointer.
        :param data: The actual data of the pointer.
        :param anchor: The address from which the game derives the destination. If None, will use the beginning of
         the position's bank.
        :raises ValueError: Raised when neither the data nor the destination is provided.
        :raises ImpossibleDestination: Raised when the destination is not in the same bank as the anchor.
        """

        if destination is None and data is None:
            raise ValueError("Either provide the destination or the data.")

        super().__init__(position=position)
        self.anchor = anchor or Bytes.from_position(self.position.bank())
        self.is_relative = bool(anchor)
        self.destination = destination if destination is not None else self._data_to_destination(data=data)

        if (anchor and self.destination < anchor) or self.anchor.bank() != self.destination.bank():
            raise ImpossibleDestination(
                f"Destination '{destination.to_snes_address()}' can't be reached with pointer's"
                f" anchor at '{self.anchor.to_snes_address()}'. "
            )

    @classmethod
    def from_match(cls, match: Match, position: Bytes, labels: list[Label], anchor: Bytes | None = None) -> Self:
        """
        :param match: A regex.Match object that matched Regex.POINTER_LINE.
        :param position: The position of the Pointer object.
        :param labels: A list of labels used to determine the destination.
        :param anchor: The address from which the game derives the destination.
        :return: A Pointer object.
        """
        data, destination = None, None

        if label_name := match.group("label"):
            destination = cls.find_destination(label_name, labels)
        else:
            data = Bytes.from_str(match.group("number"))

        is_relative = match.group("is_relative")
        anchor = anchor if is_relative else None

        return cls(position=position, destination=destination, data=data, anchor=anchor)

    @classmethod
    def from_bytes(cls, value: bytes, position: Bytes | None = None, anchor: Bytes | None = None) -> Self:
        """
        Converts a bytes array into a Pointer.
        :param value: A bytes array representing the data of the Pointer.
        :param position: The position of the Pointer.
        :param anchor: The address from which the game derives the destination.
        :return: A Pointer.
        """
        return Pointer(position=position, data=Bytes.from_bytes(value), anchor=anchor)

    @property
    def data(self) -> Bytes:
        """
        Calculates the data out of the destination and the anchor, if it exists.
        :return: A Bytes object of length 2.
        """
        delta = int(self.destination) - int(self.anchor)
        return Bytes.from_int(delta, length=2)

    def to_line(
        self, show_address: bool = False, labels: list[Label] | None = None, current_anchor: Bytes | None = None
    ) -> str:
        """
        Converts a Pointer into a script line.
        :param show_address: When True, will add the Pointer's position as a comment.
        :param labels: A list of labels in order to represent the destination as a label and not a SNES address.
        :param current_anchor: If the Pointer is relative and the current_anchor is different from the Pointer's one,
         an anchor line will be prepended to the output.
        :return: A string.
        """
        output = ""
        destination_label, anchor_label = None, None

        if labels:
            destination_label = self.find_label(destination=self.destination, labels=labels)
            anchor_label = self.find_label(destination=self.anchor, labels=labels)

        if self.is_relative and current_anchor and current_anchor != self.anchor:
            output += "\n#"
            output += f"{anchor_label.name}" if anchor_label else f"${self.anchor.to_snes_address()}"
            output += "\n"

        output += f"  {'r' if self.is_relative else ''}ptr "
        output += f"{destination_label.name}" if destination_label else f"${self.data}"
        output += f" ; {self.position.to_snes_address()}" if show_address else ""

        return output

    def __bytes__(self) -> bytes:
        """
        Converts the Pointer into a bytes array.
        :return: The bytes array corresponding to the data.
        """
        return bytes(self.data)

    def __eq__(self, other: Self) -> bool:
        return self.position == other.position and self.destination == other.destination

    def __str__(self) -> str:
        return f"ptr ${self.data}"

    def __repr__(self) -> str:
        return (
            "Pointer("
            f"position=0x{str(self.position)}, "
            f"data=0x{str(self.data)}, "
            f"destination=0x{str(self.destination)}, "
            f"anchor=0x{str(self.anchor)}"
            ")"
        )

    def __len__(self) -> int:
        return 2

    def _data_to_destination(self, data: Bytes) -> Bytes:
        """
        Converts the data of the Pointer into the intended destination.
        :param data: A Bytes object of length 2.
        :return: The destination of the pointer as a Bytes object.
        """
        instance = Bytes.from_position(int(data) + int(self.anchor))
        return instance
