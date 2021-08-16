import logging
import re
from typing import Union

from src.lib.structures.asm.label import Label
from src.lib.structures import Bytes
from src.lib.structures.asm.opcodes import Opcodes

BRANCHING_OPCODES = {
    0x10: "BPL",
    0x30: "BMI",
    0x50: "BVC",
    0x70: "BVS",
    0x80: "BRA",
    0x82: "BRL",
    0x90: "BCC",
    0xB0: "BCS",
    0xD0: "BNE",
    0xF0: "BEQ",
}


class Instruction:
    def __new__(cls, *args, **kwargs):
        opcode = Bytes(kwargs["opcode"]) if "opcode" in kwargs else int(args[0])
        if int(opcode) in BRANCHING_OPCODES.keys():
            return super().__new__(BranchingInstruction)
        return super().__new__(cls)

    def __init__(
        self,
        opcode: Union[Bytes, int, str, bytes],
        data: Union[Bytes, int, str, bytes] = None,
        position: Union[Bytes, int, str, bytes] = None,
        comment: str = None,
        m: bool = False,
        x: bool = False,
        label: Label = None,
        length: int = None,
        endianness: str = "little",
    ):

        self.opcode = Bytes(opcode)
        if length:
            self.data = Bytes(data, length=length, endianness=endianness)
        else:
            self.data = Bytes(data, endianness=endianness)
        self.position = Bytes(position)
        self.comment = comment
        self.m = m
        self.x = x
        self.label = label

    @classmethod
    def from_line(
        cls,
        command: str,
        chunk: str = None,
        position: int = None,
        comment: str = None,
        m: bool = False,
        x: bool = False,
        destination_label: Label = None,
    ):
        if command == "MVP":
            match = re.search(r"\$([0-9A-F]{2}),\$([0-9A-F]{2})", chunk)
            data = "".join([match.group(1), match.group(2)])
            logging.warning("This part has been untested.")
            return cls(
                opcode=0x44,
                data=data,
                position=position,
                m=m,
                x=x,
                comment=comment,
                length=2,
            )
        opcode = cls.find_opcode(command, chunk, m, x)
        length = opcode[1]["length"] - opcode[1]["m"] * m - opcode[1]["x"] * x
        if command not in BRANCHING_OPCODES.values() or (
            command in BRANCHING_OPCODES.values() and cls.is_branching_chunk_data(chunk)
        ):
            instruction = cls(
                opcode=opcode[0],
                data=cls.reverse_pairs(cls.get_data(chunk)),
                position=position,
                m=m,
                x=x,
                comment=comment,
                length=length,
            )
            return instruction
        elif cls.is_branching_chunk_destination(chunk):
            destination = int(chunk.replace("$", ""), 16)
            return cls(
                opcode=opcode[0],
                data=cls.destination_to_data(command, destination, position),
                position=position,
                m=m,
                x=x,
                comment=comment,
                length=length,
            )
        else:
            return cls(
                opcode=opcode[0],
                data=cls.destination_to_data(command, destination_label.position, position),
                position=position,
                m=m,
                x=x,
                comment=comment,
            )

    @staticmethod
    def is_branching_chunk_data(chunk):
        return re.match(r"#\$([0-9A-F]{2}){1,2}", chunk)

    @staticmethod
    def is_branching_chunk_destination(chunk):
        return re.match(r"\$[0-9A-F]{4}", chunk)

    @staticmethod
    def extract_instruction_length_from_line(line: str) -> int:
        matches = re.search(r"^ *(\w{3})( +([^( ]+))?", line)
        if matches.group(1) == "BRL":
            return 3
        elif matches.group(1) in BRANCHING_OPCODES.values():
            return 2
        elif matches.group(3):
            return len(re.sub(r"[ #\$\(\)\[\],SXY]", "", matches.group(3))) // 2 + 1
        else:
            return 1

    @classmethod
    def find_opcode(cls, command: str, chunk: str, m: bool, x: bool):
        if chunk is None:
            chunk = ""
        opcodes = {opcode: instruction for opcode, instruction in Opcodes.items() if instruction["command"] == command}
        if command not in BRANCHING_OPCODES.values() or (
            command in BRANCHING_OPCODES.values() and cls.is_branching_chunk_data(chunk)
        ):
            data_str = cls.get_data(chunk)
            length = int(len(data_str) / 2)
            mode = chunk.replace(data_str, "_")
            opcodes = [
                (opcode, instruction)
                for opcode, instruction in opcodes.items()
                if instruction["mode"] == mode
                and instruction["length"] - instruction["m"] * m - instruction["x"] * x == length
            ]
        else:
            opcodes = [(opcode, instruction) for opcode, instruction in opcodes.items()]

        if not opcodes:
            raise ValueError(
                f"Can't find an opcode with the following information: {command=}, {length=}, {mode=}, {m=}, {x=}."
            )
        if len(opcodes) > 1:
            raise ValueError(
                "Found too many opcodes that satisfies the following information: "
                f"{command=}, {length=}, {mode=}, {m=}, {x=}. Opcodes={opcodes}"
            )
        return opcodes[0]

    @classmethod
    def get_data(cls, chunk: str) -> str:
        if chunk:
            return re.sub(r"[$#,\(\)\[\]SXY]", "", chunk)
        else:
            return ""

    @property
    def command(self):
        return Opcodes[int(self.opcode)]["command"]

    @property
    def bank(self):
        return self.position // 0x010000

    @property
    def address(self):
        return self.position.to_address()

    @property
    def length(self):
        code = Opcodes[int(self.opcode)]
        return code["length"] - code["m"] * self.m - code["x"] * self.x

    @property
    def details(self):
        details = Opcodes[int(self.opcode)]["mode"]
        if self.opcode == 0x44:
            return f"${self.data[0]:02X},${self.data[1]:02X}"
        else:
            return details.replace("_", self.data.string("big"))

    @classmethod
    def destination_to_data(cls, command, destination, position):
        if command == "BRL":
            delta = (destination - position - 0x03) % 0x010000
            data = Bytes(delta, length=2, endianness="little")
        else:
            delta = (destination - position + 0x100 - 0x02) % 0x0100
            data = Bytes(delta, length=1, endianness="little")
        return data

    def __str__(self):
        response = ""
        if self.label:
            response += f"\n{self.label}"
            if self.label.name == "start":
                response += f"={self.address}"
            response += "\n"
        response += f"  {self.command} {self.details.ljust(10, ' ')}"
        if self.comment:
            response += f' "{self.comment}"'
        return response

    @property
    def debug_string(self):
        return (
            f"{self.address} {str(self.opcode)}{self.data.string('little').ljust(6, ' ')} "
            f"{self.command} {self.details.strip()}"
        )

    @staticmethod
    def reverse_pairs(string):
        reverse_string = string[::-1]
        return "".join([reverse_string[2 * i + 1] + reverse_string[2 * i] for i in range(len(reverse_string) // 2)])


class BranchingInstruction(Instruction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._destination = None
        self._destination_label = None

    @property
    def destination_label(self):
        return self._destination_label

    @destination_label.setter
    def destination_label(self, label: Label):
        self._destination_label = label
        self.destination_to_data(self.command, self._destination_label.position, self.position)

    @property
    def destination(self):
        if self.data.value is not None:
            offset = int(self.data)
            if self.opcode == 0x82:
                self._destination = (offset + 0x8000) % 0x010000 + int(self.position) - 0x7FFD
            else:
                self._destination = (offset + 0x80) % 0x0100 + int(self.position) - 0x7E
            return self._destination
        return None

    @destination.setter
    def destination(self, destination):
        self._destination = destination % 0x010000 + self.bank
        self.data = self.destination_to_data(
            command=self.command,
            destination=self._destination,
            position=self.position,
        )

    def __str__(self):
        response = f"  {self.command}"

        if self.destination_label:
            response += f" {self.destination_label.name.ljust(10, ' ')}"
        elif self.destination:
            destination = f" {self.destination:02X}"[-4:]
            response += f" ${destination.ljust(10, ' ')}"
        else:
            response += f" {self.details.ljust(10, ' ')}"
        if self.comment:
            response += f" ({self.comment})"
        return response

    @property
    def debug_string(self):
        if self.destination:
            return (
                f"{self.address} {str(self.opcode)}{self.data.string('little').ljust(6, ' ')} "
                f"{self.command} ${self.destination:02X}"
            )
        else:
            return super().__str__()
