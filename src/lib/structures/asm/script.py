import logging
import re
from typing import List, Union

from src.lib.structures.fields import Binary, Instruction, Bytes, Label
from src.lib.structures.fields import BRANCHING_OPCODES, BranchingInstruction


class Script:
    def __init__(self, m:bool = False, x: bool = False):
        self.instructions = []
        self.labels = set()
        self.m = m
        self.x = x

    def assemble(self, pad: bool = True):
        if pad and self.get_label(by="name", value="end"):
            self.pad()
        for instruction in self.instructions:
            logging.debug(
                f"Writing {instruction.debug_string} @ {instruction.address}"
            )
            start = int(instruction.position)
            end = start + 1 + len(instruction.data)
            Binary()[start:end] = bytes(instruction.opcode) + bytes(instruction.data)

    @classmethod
    def disassemble(
        cls,
        start: int,
        last_instruction_position: int,
        m: bool = False,
        x: bool = False
    ):
        script = cls(m=m, x=x)
        script.labels.add(Label(position=Bytes(start), name="start"))
        script.labels.add(Label(position=Bytes(last_instruction_position + 1), name="end"))
        position = start
        while position <= last_instruction_position:
            instruction = Instruction(
                opcode=Binary()[position],
                position=position,
                m=m,
                x=x,
            )
            position += 1
            if instruction.length:
                read_bytes = Binary()[position:position + instruction.length]
                instruction.data = Bytes(
                    read_bytes, length=instruction.length, endianness="little"
                )
            position += instruction.length
            if type(instruction) == BranchingInstruction:
                script.labels.add(
                    Label(
                        position=Bytes(instruction.destination),
                        name=f"label_{instruction.destination % 0x010000:02X}",
                    )
                )
            script.instructions.append(instruction)
            m, x = script.update_flags(instruction, m, x)
        script.assign_labels()
        return script

    def to_script(self, filename: str):
        file_content = f"m={str(self.m).lower()},x={str(self.x).lower()}\n"
        labels_before_script = sorted([
            label
            for label in self.labels
            if label < self.get_label(by="name", value="start")
        ])
        file_content += "\n".join([
            f"{label.name}={label.position.to_address()}"
            for label in labels_before_script
        ])
        file_content += "\n"

        for instruction in self.instructions:
            file_content += f"{instruction}\n"

        end_label = self.get_label(by="name", value="end")
        file_content += f"\nend={end_label.position.to_address()}\n\n"

        labels_after_script = sorted([
            label
            for label in self.labels
            if label > self.get_label(by="name", value="end")
        ])

        file_content += "\n".join([
            f"{label.name}={label.position.to_address()}"
            for label in labels_after_script
        ])

        with open(filename, "w") as f:
            f.write(file_content)

    @classmethod
    def from_script(cls, filename: str):
        script = cls()
        with open(filename, "r") as f:
            lines = [line for l in f.readlines() if (line := l.rstrip())]
            script.labels = script.extract_labels(lines)
            script.instructions = script.extract_instructions(lines)
        return script

    @staticmethod
    def extract_labels(lines):
        labels = set()
        for line in lines:
            fixed_position = False
            if match := re.search(r"^([\w\d_]+)(=([C-F][0-9A-F]/[0-9A-F]{4}))?$", line):
                if match.group(2):
                    position = Bytes.from_address(match.group(3))
                    fixed_position = True
                name = match.group(1)
                labels.add(Label(position=position, name=name, fixed_position=fixed_position))
            elif re.search(r"^m=(\w+),x=(\w+)", line):
                continue
            else:
                position += Instruction.extract_instruction_length_from_line(line)
        logging.debug(labels)
        return labels

    def extract_instructions(self, lines: List[str]):
        instructions = []
        position = self.get_label(by="name", value="start").position
        for line in lines:
            if match := re.search(r" +(\w{3})( +([^ \"]*))?( *\"([^\)]*)\")?", line):
                command = match.group(1)
                chunk = match.group(3)
                comment = match.group(5)
                logging.debug(chunk)
                if command in BRANCHING_OPCODES.values():
                    destination_label = self.get_label(by="name", value=chunk)
                else:
                    destination_label = None
                instruction = Instruction.from_line(
                    command=command,
                    chunk=chunk,
                    comment=comment,
                    position=position,
                    m=m,
                    x=x,
                    destination_label=destination_label,
                )
                instruction.label = self.get_label(
                    by="position", value=instruction.position
                )
                position += instruction.length + 1
                m, x = self.update_flags(instruction, m, x)
                instructions.append(instruction)
            elif match := re.search(r"^[\w\d_]+=([C-F][0-9A-F]/[0-9A-F]{4})$", line):
                position = Bytes.from_address(match.group(1))
            elif match := re.search(r"^m=(\w+),x=(\w+)", line):
                m = True if match.group(1).lower() == "true" else False
                x = True if match.group(2).lower() == "true" else False
        return instructions

    @staticmethod
    def update_flags(instruction: Instruction, m: bool, x: bool):
        if int(instruction.opcode) == 0xC2:
            flags = int(instruction.data)
            m = not bool(flags & 0x20)
            x = not bool(flags & 0x10)
        elif int(instruction.opcode) == 0xE2:
            flags = int(instruction.data)
            m = bool(flags & 0x20)
            x = bool(flags & 0x10)
        return m, x

    def assign_labels(self):
        for instruction in self.instructions:
            if not instruction.label:
                instruction.label = self.get_label(
                    by="position", value=instruction.position
                )
                if instruction.label:
                    logging.info(f"Label found: {instruction.label.name}")
            if type(instruction) == BranchingInstruction:
                if instruction.destination:
                    instruction.destination_label = self.get_label(
                        by="position", value=instruction.destination
                    )
                else:
                    instruction.destination_label = self.get_label(
                        by="name", value=instruction.destination_label_name
                    )
                    instruction.set_data()

    def get_label(self, by: str, value: Union[int, str]):
        for label in self.labels:
            if value == getattr(label, by):
                return label
        return None

    def pad(self, opcode: int = 0xEA):
        last_position = self.instructions[-1].position + self.instructions[-1].length + 1
        for offset in range(int(self.get_label(by="name", value="end").position - last_position)):
            self.instructions.append(Instruction(opcode=opcode, position=offset + last_position))
