import re
from re import Match
from typing import Self

from src.lib.misc.exception import TooManyCandidatesException, NoCandidateException
from src.lib.structures.asm.flags import Flags
from src.lib.structures.asm.label import Label
from src.lib.structures.asm.opcodes import Opcodes
from src.lib.structures.asm.regex import Regex, ToLineMixin
from src.lib.structures.asm.script_line import ScriptLine, DataMixin, BankMixin, ImpossibleDestination, DestinationMixin
from src.lib.structures.bytes import Bytes, Endian, Position, BytesType


class Instruction(ScriptLine, DataMixin, ToLineMixin):
    def __init__(self, opcode: BytesType, position: Position | None = None, data: Bytes | None = None):
        super().__init__(position=position)
        self.opcode = opcode
        self.data = data

    @classmethod
    def from_regex_match(cls, match: Match, position: Position, flags: Flags) -> Self:
        command = match.group("command")
        mode = cls.mode(match)
        data, length = None, 0

        if (data := cls.data(match)) is not None:
            data = Bytes(data)
            length = len(data)

        opcode = cls.find_opcode(command=command, mode=mode, length=length, flags=flags)

        return cls(position=position, opcode=opcode, data=data)

    @classmethod
    def from_bytes(cls, value: bytes, position: Position = None, flags: Flags = None) -> Self:
        flags = flags or Flags()
        value = Bytes(value, in_endian=Endian.BIG)
        command = Opcodes[int(value[0])]
        length = command["length"] - flags.m * command["m"] - flags.x * command["x"]
        data = Bytes(value[1 : length + 1]) if length else None
        opcode = Bytes(value[0])

        if cls._is_branching_instruction(opcode):
            return BranchingInstruction(position=position, opcode=Bytes(value[0]), data=data)
        else:
            return Instruction(position=position, opcode=Bytes(value[0]), data=data)

    @classmethod
    def _is_branching_instruction(cls, opcode: Bytes):
        return cls.command(opcode) in [
            "JMP",
            "JML",
            "JSR",
            "JSL",
            "BCC",
            "BCS",
            "BEQ",
            "BMI",
            "BNE",
            "BPL",
            "BRA",
            "BRL",
            "BVC",
            "BVS",
        ]

    def __bytes__(self) -> bytes:
        output = bytes(self.opcode)
        if self.data is not None:
            output += bytes(self.data)
        return output

    def to_line(self, show_address: bool = False, labels: list[Label] | None = None) -> str:
        output = f"  {self}"
        output += f" # {self.position.to_snes_address()}" if show_address else ""
        return output

    @staticmethod
    def mode(match: Match) -> str:
        if match is None or (data := match.group("chunk")) is None:
            return "_"

        return re.sub(Regex.DATA, "_", data)

    @staticmethod
    def find_opcode(command: str, mode: str, length: int, flags: Flags) -> Bytes:
        candidates = list()
        for code, operation in Opcodes.items():
            if operation["command"] == command and operation["mode"] == mode:
                effective_length = operation["length"] - operation["m"] * flags.m - operation["x"] * flags.x
                if effective_length == length:
                    candidates.append(code)

        if len(candidates) > 1:
            raise TooManyCandidatesException(f"More than one candidate for {command=} and {mode=}. {candidates=}")
        if len(candidates) == 0:
            raise NoCandidateException(f"No candidate was found for {command=}, {mode=} and {length=}.")

        return Bytes(candidates[0])

    @staticmethod
    def command(opcode: Bytes) -> str:
        return Opcodes[int(opcode)]["command"]

    def is_flag_setter(self) -> bool:
        return self.command(self.opcode) in ["REP", "SEP"]

    def set_flags(self, flags: Flags) -> Flags:
        flag_state = True if self.command(self.opcode) == "SEP" else False
        if int(self.data) & 0x10:
            flags.x = flag_state
        if int(self.data) & 0x20:
            flags.m = flag_state
        return flags

    def __len__(self) -> int:
        if self.data is None:
            return 1
        return len(self.data) + 1

    def __eq__(self, other: Self) -> bool:
        return self.position == other.position and self.opcode == other.opcode and self.data == other.data

    def __str__(self) -> str:
        output = Opcodes[int(self.opcode)]["command"]
        mode = Opcodes[int(self.opcode)]["mode"]
        if mode == "#$_,#$_":
            output += f" #${str(self.data[1])},#${str(self.data[0])}"
        elif self.data:
            output += " " + mode.replace("_", str(self.data))
        return output

    def __repr__(self) -> str:
        return f"{self.position}: {self} ({self.opcode} {self.data})"


class BranchingInstruction(Instruction, BankMixin, DestinationMixin):
    def __init__(self, position: Position, opcode: Bytes, data: Bytes = None, destination: Position = None):
        if data is None and destination is None:
            raise ValueError("Please provide either data or destination.")
        super().__init__(position=position, opcode=opcode)
        self.data = data if data is not None else self.destination_to_data(destination=destination)
        self.destination = destination if destination is not None else self.data_to_destination(data=data)

    @classmethod
    def from_regex_match(cls, match: Match, position: Position, labels: list[Label]) -> Self:
        command = match.group("command")
        data, destination = None, None

        if label_name := match.group("label"):
            destination = cls.find_destination(label_name, labels)
            mode = cls.command_to_mode(command)

            if not cls.is_destination_possible(position, destination, command):
                raise ImpossibleDestination(
                    f"Destination '{destination.to_snes_address()}' can't be reached with pointer"
                    f" at position '{position.to_snes_address()}'"
                )

            length = cls.find_length(command=command)
        else:
            data = Bytes(cls.data(match))
            mode = cls.mode(match)
            length = len(data)

        opcode = cls.find_opcode(command=command, mode=mode, length=length, flags=Flags())

        return cls(position=position, opcode=opcode, data=data, destination=destination)

    @classmethod
    def is_destination_possible(cls, position: Position, destination: Position, command: str) -> bool:
        if command in ["JMP", "JML", "JSL"]:
            return True
        if command in ["BRL", "JSR"]:
            return cls.bank(position) == cls.bank(destination)
        return int(position) - 0x7E <= int(destination) <= int(position) + 0x81

    def data_to_destination(self, data: Bytes) -> Position:
        command = self.command(self.opcode)
        if command in ["JSL", "JML"]:
            return Position(value=data)
        if command in ["JMP", "JSR"]:
            return Position(value=int(data) + self.position.bank())
        if command == "BRL":
            return Position(value=(int(data) + 0x8000) % 0x010000 + int(self.position) - 0x7FFD)
        return Position(value=(int(data) + 0x80) % 0x0100 + int(self.position) - 0x7E)

    def destination_to_data(self, destination: Position) -> Bytes:
        command = self.command(self.opcode)
        if command in ["JSL", "JML"]:
            return Bytes(value=destination, out_endian=Endian.LITTLE)
        if command in ["JMP", "JSR"]:
            return Bytes(value=int(destination[1:]), length=2)
        if command == "BRL":
            return Bytes(value=(int(destination) - int(self.position) - 3) % 0x010000, length=2)
        return Bytes(value=((int(destination) - int(self.position) % 0x0100) - 2) % 0x0100, length=1)

    @classmethod
    def find_length(cls, command: str) -> int:
        if command in ["BRL", "JSR", "JMP"]:
            return 2
        if command.startswith("B"):
            return 1
        return 3  # JSL, JML

    @classmethod
    def command_to_mode(cls, command: str) -> str:
        if command.startswith("B"):
            return "#$_"
        return "$_"

    def to_line(self, show_address: bool = False, labels: list[Label] | None = None) -> str:
        output = f"  {Opcodes[int(self.opcode)]['command']}"
        label = None

        if labels:
            label = self.find_label(destination=self.destination, labels=labels)

        if label:
            output += f" {label.name}"
        else:
            mode = Opcodes[int(self.opcode)]["mode"]
            output += f" {mode.replace('_', str(self.data))}"

        output += f" # {self.position.to_snes_address()}" if show_address else ""
        return output
