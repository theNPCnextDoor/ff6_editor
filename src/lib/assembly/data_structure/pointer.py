import logging
from typing import Self

from src.lib.assembly.artifact.variables import Variables
from src.lib.assembly.data_structure.instruction.operand import Operand, OperandType
from src.lib.assembly.bytes import Bytes

from src.lib.assembly.data_structure.data_structure import DataStructure
from src.lib.misc.exception import ImpossibleDestination


class Pointer(DataStructure):
    """
    Pointers are used in the script to point to an element in a list containing elements of varying sizes. Pointers can
     either be direct, where they can point to anywhere in the same bank at the pointer itself. Or they can be relative,
     where they can point to anywhere from an anchor to the end of said anchor's bank.
    """

    def __init__(
        self,
        operand: Operand,
        position: Bytes | None = None,
        anchor: Operand | None = None,
    ):
        super().__init__(position=position)
        self.anchor = anchor
        self.operand = operand

    @property
    def is_relative(self) -> bool:
        return bool(self.anchor)

    @property
    def destination(self) -> Bytes:
        """
        Determines the destination of the Pointer. It is either derived from the value and the Pointer's bank
        when the Pointer is direct, or it is the value of the anchor plus the value of the Pointer.
        :return: A Bytes object.
        """
        if self.operand.variable:
            return self.operand.variable.value
        if self.anchor:
            return Bytes.from_position(int(self.anchor.value) + int(self.operand.value))
        return Bytes.from_position(self.position.bank() + int(self.operand.value))

    @classmethod
    def from_line(
        cls, operand: str, position: Bytes, anchor: Operand | None = None, labels: Variables | None = None
    ) -> Self:
        """
        Converts a script line into a Pointer.
        :param operand: The destination of the pointer as a word (2-bytes object).
        :param position: The position of the Pointer.
        :param labels: A list of labels used to determine the destination.
        :param anchor: The address from which the game derives the destination.
        :return: A Pointer.
        :raises ImpossibleDestination: Raised when the destination can't be reached from either the Pointer's position
        or its anchor, when it exists.
        """
        parent_position = anchor.value if anchor else Bytes.from_position(position.bank())
        _operand = Operand.from_line(
            value=operand, parent_position=parent_position, operand_type=OperandType.DEFAULT, variables=labels
        )

        if anchor and _operand.variable:
            _operand.value -= int(anchor.value) % 0x010000

        if _operand.variable:
            destination = _operand.variable.value
        elif anchor:
            destination = Bytes.from_position(int(anchor.value) + int(_operand.value))
        else:
            destination = Bytes.from_position(int(position.bank()) + int(_operand.value))

        if destination < parent_position or destination.bank() != parent_position.bank():
            message = (
                f"Destination '{destination.to_snes_address()}' can't be reached with pointer's"
                f" {'anchor' if anchor else 'position'} at '{parent_position.to_snes_address()}'. "
            )
            logging.error(message)
            raise ImpossibleDestination(message)

        pointer = cls(position=position, operand=_operand, anchor=anchor)
        logging.debug(f"Created {repr(pointer)}.")
        return pointer

    @classmethod
    def from_bytes(cls, value: bytes, position: Bytes, anchor: Bytes | None = None) -> Self:
        """
        Converts bytes into a Pointer.
        :param value: The bytes representing the data of the Pointer.
        :param position: The position of the Pointer.
        :param anchor: The address from which the game derives the destination.
        :return: A Pointer.
        """
        operand = Operand(Bytes.from_bytes(value))

        pointer = Pointer(position=position, operand=operand, anchor=anchor)
        logging.debug(f"Created {repr(pointer)}.")
        return pointer

    def to_line(
        self, show_address: bool = False, labels: Variables | None = None, current_anchor: Bytes | None = None
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
        anchor_label = None

        if labels and self.anchor:
            anchor_label = labels.find_by_position(self.anchor.value)

        if self.is_relative and current_anchor and current_anchor != self.anchor:
            output += "\n#"
            output += f"{anchor_label.name}" if anchor_label else f"${self.anchor.value.to_snes_address()}"
            output += "\n"

        output += f"  {'r' if self.is_relative else ''}ptr {str(self.operand)}"
        output += f" ; {self.position.to_snes_address()}" if show_address else ""

        return output

    def __eq__(self, other: Self) -> bool:
        return self.position == other.position and self.operand == other.operand and self.anchor == other.anchor

    def __bytes__(self) -> bytes:
        return bytes(self.operand)

    def __str__(self) -> str:
        return f"ptr {self.operand}"

    def __repr__(self) -> str:
        output = (
            "Pointer("
            f"position=0x{self.position}, "
            f"as_str='{str(self)}', "
            f"as_bytes={bytes(self)}, "
            f"as_hexa=0x{str(self.operand.value)}, "
            f"destination=0x{self.destination}"
        )
        if self.operand.variable:
            output += f", operand_var={repr(self.operand.variable)}"
        if self.anchor:
            output += f", anchor=0x{self.anchor.value}"
            if self.anchor.variable:
                output += f", anchor_var={repr(self.anchor.variable)}"
        output += ")"
        return output

    def __len__(self) -> int:
        return 2

    @classmethod
    def find_length(cls) -> int:
        """
        Determines the length of the script line during the pre-parsing phase. However, a Pointer is always 2 bytes.
        :return: 2
        """
        length = 2
        logging.debug(f"Pointer length is always {length}.")
        return length
