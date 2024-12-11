from __future__ import annotations
import re
from enum import Enum, auto
from pathlib import Path
from typing import Self

from src.lib.structures.asm.pointer import Pointer
from src.lib.structures.asm.instruction import BranchingInstruction, Instruction
from src.lib.structures.asm.flags import Flags
from src.lib.structures.asm.label import Label
from src.lib.structures.asm.regex import Regex
from src.lib.structures.asm.script_line import ScriptLine
from src.lib.structures.bytes import BytesType, Position


class ScriptMode(Enum):
    INSTRUCTIONS = auto()
    POINTERS = auto()

class ScriptSection:
    def __init__(self, start: BytesType, end: BytesType, mode: ScriptMode, flags: Flags = None):
        self.start = start
        self.end = end
        self.mode = mode
        self.flags = flags or Flags()


class Script:
    def __init__(self):
        self.instructions = list()
        self.branching_instructions = list()
        self.pointers = list()
        self.labels = list()

    @classmethod
    def from_script_file(cls, filename: str | Path, flags: Flags = None) -> Self:
        with open(filename) as f:
            lines = f.readlines()

        script = cls()

        cursor = 0
        flags = flags or Flags()
        lines_with_labels = list()

        for line in lines:
            if match := re.search(Regex.FLAGS, line):
                flags = Flags.from_regex_match(match=match)

            elif match := re.search(Regex.LABEL_LINE, line):
                label = Label.from_regex_match(match=match, position=Position(cursor))
                cursor = int(label.position)
                script.labels.append(label)

            elif re.search(Regex.POINTER, line):
                lines_with_labels.append((line, cursor))
                cursor += 2

            elif match := re.search(Regex.BRANCHING_INSTRUCTION, line):
                command = match.group("command")

                if match.group("label"):
                    lines_with_labels.append((line, cursor))
                else:
                    instruction = BranchingInstruction.from_regex_match(match=match, position=Position(cursor))
                    script.branching_instructions.append(instruction)

                cursor += BranchingInstruction.find_length(command=command) + 1

            elif match := re.match(Regex.INSTRUCTION, line):
                instruction = Instruction.from_regex_match(match=match, position=Position(cursor), flags=flags)
                cursor += len(instruction)
                script.instructions.append(instruction)

                if instruction.is_flag_setter():
                    flags = instruction.set_flags(flags)

        for line, cursor in lines_with_labels:
            if match := re.match(Regex.BRANCHING_INSTRUCTION, line):
                instruction = BranchingInstruction.from_regex_match(match=match, position=Position(cursor), labels=script.labels)
                script.branching_instructions.append(instruction)

            elif match := re.match(Regex.POINTER, line):
                pointer = Pointer.from_regex_match(match=match, position=Position(cursor), labels=script.labels)
                script.pointers.append(pointer)

        script.instructions.sort()
        script.branching_instructions.sort()
        script.pointers.sort()

        return script

    def to_script_file(self, filename: str | Path, flags: Flags):
        self._extract_labels()
        lines = self.labels + self.pointers + self.instructions + self.branching_instructions
        lines.sort(key=lambda x: ScriptLine.sort(x))
        output = [flags.to_line()]

        cursor = int(lines[0].position)

        if not isinstance(lines[0], Label):
            start_label = Label(name="start", position=lines[0].position)
            self.labels.append(start_label)
            output.append(start_label.to_line(show_address=True))

        output.append(lines[0].to_line(show_address=True))
        cursor += len(lines[0])

        for line in lines[1:]:
            if cursor != int(line.position):
                if isinstance(line, Label):
                    output.append(line.to_line(show_address=True))
                    continue

                label = Label(position=line.position)
                self.labels.append(label)
                output.append(label.to_line(show_address=True))

            output.append(line.to_line(labels=self.labels))
            cursor = int(line.position) + len(line)

        with open(filename, "w") as f:
            f.write("\n".join(output))

    def to_rom(self, filename: str) -> None:
        with open(filename, "rb+") as f:
            for pointer in self.pointers:
                f.seek(int(pointer.position))
                f.write(bytes(pointer))
            for instruction in self.instructions:
                f.seek(int(instruction.position))
                f.write(bytes(instruction))
            for branching_instruction in self.branching_instructions:
                f.seek(int(branching_instruction.position))
                f.write(bytes(branching_instruction))

    @classmethod
    def from_rom(cls, filename: str | Path, sections: list[ScriptSection]) -> Self:
        script = cls()
        with open(filename, "rb") as f:
            for section in sections:
                cursor = section.start
                f.seek(cursor)

                if section.mode == ScriptMode.POINTERS:
                    while cursor < section.end:
                        pointer_bytes = f.read(2)
                        pointer = Pointer.from_bytes(position=Position(cursor), value=pointer_bytes)
                        script.labels.append(Label(position=Position(pointer.destination)))
                        script.pointers.append(pointer)
                        cursor += 2

                elif section.mode == ScriptMode.INSTRUCTIONS:
                    flags = section.flags
                    while cursor < section.end:
                        f.seek(cursor)
                        value = f.read(4)

                        instruction = Instruction.from_bytes(position=Position(cursor), value=value, flags=flags)

                        if isinstance(instruction, BranchingInstruction):
                            script.branching_instructions.append(instruction)
                            label = Label(position=Position(instruction.destination))
                            if label not in script.labels:
                                script.labels.append(label)
                        else:
                            if instruction.is_flag_setter():
                                flags = instruction.set_flags(flags)

                            script.instructions.append(instruction)
                        cursor += len(instruction)

        script.labels = list(set(sorted(script.labels)))
        script.pointers.sort()
        script.instructions.sort()
        script.branching_instructions.sort()

        return script

    def _extract_labels(self):
        for script_line in self.pointers + self.branching_instructions:
            label = Label(position=script_line.destination)
            if label not in self.labels:
                self.labels.append(label)
