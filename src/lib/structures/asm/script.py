from __future__ import annotations
import re
from enum import Enum, auto
from pathlib import Path
from typing import Self, BinaryIO

from src.lib.misc.exception import MissingSectionAttribute
from src.lib.structures.asm.blob import Blob
from src.lib.structures.asm.pointer import Pointer
from src.lib.structures.asm.instruction import BranchingInstruction, Instruction
from src.lib.structures.asm.flags import Flags
from src.lib.structures.asm.label import Label
from src.lib.structures.asm.regex import Regex
from src.lib.structures.asm.string import String
from src.lib.structures.asm.script_line import ScriptLine
from src.lib.structures.bytes import BytesType, Position
from src.lib.structures.charset.charset import MENU_CHARSET, Charset


class ScriptMode(Enum):
    INSTRUCTIONS = auto()
    POINTERS = auto()
    BLOBS = auto()
    MENU_STRINGS = auto()


class ScriptSection:
    def __init__(self, start: BytesType, end: BytesType, mode: ScriptMode, **attributes):
        self.start = start
        self.end = end
        self.mode = mode
        self.attributes = attributes


class Script:
    def __init__(self):
        self.blobs = list()
        self.branching_instructions = list()
        self.instructions = list()
        self.labels = list()
        self.pointers = list()

    @classmethod
    def from_script_file(cls, filename: str | Path, flags: Flags | None = None, charset: Charset | None = None) -> Self:
        with open(filename) as f:
            lines = f.readlines()

        script = cls()

        cursor = 0
        flags = flags or Flags()
        charset = charset or Charset(charset=MENU_CHARSET)
        lines_with_labels = list()

        for line in lines:
            if match := re.search(Regex.BLOB, line):
                blob = Blob.from_regex_match(match=match, position=Position(cursor))
                cursor += len(blob)
                script.blobs.append(blob)

            elif match := re.search(Regex.MENU_STRING, line):
                string = String.from_regex_match(match=match, position=Position(cursor), charset=charset)
                cursor += len(string)
                script.blobs.append(string)

            elif match := re.search(Regex.FLAGS, line):
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
                instruction = BranchingInstruction.from_regex_match(
                    match=match, position=Position(cursor), labels=script.labels
                )
                script.branching_instructions.append(instruction)

            elif match := re.match(Regex.POINTER, line):
                pointer = Pointer.from_regex_match(match=match, position=Position(cursor), labels=script.labels)
                script.pointers.append(pointer)

        for name in ["blobs", "instructions", "branching_instructions", "pointers"]:
            _list = getattr(script, name)
            _list.sort()

        return script

    def to_script_file(self, filename: str | Path, flags: Flags) -> None:
        self._extract_labels()
        lines = self.labels + self.blobs + self.branching_instructions + self.instructions + self.pointers
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

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(output))

    def to_rom(self, filename: str) -> None:
        with open(filename, "rb+") as f:
            for line in self.blobs + self.branching_instructions + self.instructions + self.pointers:
                f.seek(int(line.position))
                f.write(bytes(line))

    @classmethod
    def from_rom(cls, filename: str | Path, sections: list[ScriptSection]) -> Self:
        script = cls()
        with open(filename, "rb") as f:
            for section in sections:
                cursor = section.start
                f.seek(cursor)

                if section.mode == ScriptMode.POINTERS:
                    cls._disassemble_pointers(cursor, f, script, section)

                elif section.mode == ScriptMode.INSTRUCTIONS:
                    cls._dissassamble_instructions(cursor, f, script, section)

                elif section.mode in (ScriptMode.BLOBS, ScriptMode.MENU_STRINGS):
                    cls._disassemble_blobs(cursor, f, script, section)

        cls._sort_lists(script)

        return script

    @classmethod
    def _disassemble_blobs(cls, cursor: int, f: BinaryIO, script: Self, section: ScriptSection) -> None:
        if section.attributes.get("length", None) is None and section.attributes.get("delimiter", None) is None:
            raise MissingSectionAttribute(
                "Attribute 'length' and 'delimiter' are missing. Please provide either of them."
                f"Attributes: {section.attributes}"
            )
        if section.mode == ScriptMode.MENU_STRINGS and not section.attributes.get("charset", None):
            raise MissingSectionAttribute(f"Attribute 'charset' is missing. Attributes: {section.attributes}")

        f.seek(cursor)
        delimiter = section.attributes.get("delimiter", None)
        while cursor < section.end:
            if length := section.attributes.get("length", None):
                data = f.read(length)
                if data == b"":
                    break
            else:
                data = b""
                while (_char := f.read(1)) != delimiter:
                    if _char == b"":
                        break
                    data += _char

            if section.mode == ScriptMode.BLOBS:
                blob = Blob.from_bytes(data=data, position=Position(cursor), delimiter=delimiter)
            else:
                blob = String.from_bytes(
                    data=data, position=Position(cursor), delimiter=delimiter, charset=section.attributes["charset"]
                )
            script.blobs.append(blob)
            cursor += len(blob)

    @classmethod
    def _disassemble_pointers(cls, cursor: int, f: BinaryIO, script: Self, section: ScriptSection) -> None:
        while cursor < section.end:
            pointer_bytes = f.read(2)
            pointer = Pointer.from_bytes(position=Position(cursor), value=pointer_bytes)
            script.labels.append(Label(position=Position(pointer.destination)))
            script.pointers.append(pointer)
            cursor += 2

    @classmethod
    def _dissassamble_instructions(cls, cursor: int, f: BinaryIO, script: Self, section: ScriptSection) -> None:
        if "flags" not in section.attributes:
            raise MissingSectionAttribute(f"Attribute 'flags' is missing. Attributes: {section.attributes}")
        flags = section.attributes["flags"]
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

    def _sort_lists(self) -> None:
        self.labels = list(set(sorted(self.labels)))
        self.blobs.sort()
        self.branching_instructions.sort()
        self.instructions.sort()
        self.pointers.sort()

    def _extract_labels(self):
        for script_line in self.pointers + self.branching_instructions:
            label = Label(position=script_line.destination)
            if label not in self.labels:
                self.labels.append(label)
