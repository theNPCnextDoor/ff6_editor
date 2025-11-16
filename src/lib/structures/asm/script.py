from __future__ import annotations
import re
from enum import Enum, auto
from pathlib import Path
from typing import Self, BinaryIO

from src.lib.misc.exception import MissingSectionAttribute
from src.lib.structures.asm.blob import Blob
from src.lib.structures.asm.blob_group import BlobGroup
from src.lib.structures.asm.pointer import Pointer
from src.lib.structures.asm.instruction import BranchingInstruction, Instruction
from src.lib.structures.asm.flags import Flags
from src.lib.structures.asm.label import Label
from src.lib.structures.asm.regex import Regex
from src.lib.structures.asm.string import String, StringTypes
from src.lib.structures.asm.script_line import ScriptLine
from src.lib.structures.bytes import Position, BEBytes, LEBytes
from src.lib.structures.charset.charset import MENU_CHARSET, DESCRIPTION_CHARSET, Charset


class ScriptMode(Enum):
    INSTRUCTIONS = auto()
    POINTERS = auto()
    BLOBS = auto()
    MENU_STRINGS = auto()
    DESCRIPTION_STRINGS = auto()
    BLOB_GROUPS = auto()


class ScriptSection:
    def __init__(self, start: int, end: int, mode: ScriptMode, **attributes):
        self.start = start
        self.end = end
        self.mode = mode
        self.attributes = attributes

    def __eq__(self, other: Self) -> bool:
        return self.start == other.start

    def __lt__(self, other: Self) -> bool:
        return self.start < other.start


class SubSection:
    def __init__(self, mode: ScriptMode, length: int | None = None, delimiter: LEBytes | None = None):
        if length is None and delimiter is None:
            raise MissingSectionAttribute("Please provide either the length or the delimiter.")
        self.mode = mode
        self.length = length
        self.delimiter = delimiter


class LabelConflict(Exception):
    pass


class LineConflict(Exception):
    pass


class Script:
    def __init__(self):
        self.blobs = list()
        self.blob_groups = list()
        self.branching_instructions = list()
        self.instructions = list()
        self.labels = list()
        self.pointers = list()

    def debug_str(self) -> str:
        lines = (
            self.blobs
            + self.blob_groups
            + self.branching_instructions
            + self.instructions
            + self.labels
            + self.pointers
        )
        output = ""
        for line in lines:
            output += f"{repr(line)}\n"
        return output

    def append_script_file(self, filename: str | Path):
        with open(filename, encoding="utf-8") as f:
            lines = f.readlines()
        lines = [stripped_line for line in lines if (stripped_line := line.rstrip())]

        cursor = 0
        flags = Flags()
        lines_with_labels = list()

        for line in lines:
            if match := re.match(Regex.DESCRIPTION_LINE, line):
                string = String.from_regex_match(match=match, position=Position.from_int(cursor))
                cursor += len(string)
                self.blobs.append(string)

            elif match := re.fullmatch(Regex.BLOB_GROUP_LINE, line):
                blob_group = BlobGroup.from_regex_match(match=match, position=Position.from_int(cursor))
                cursor += len(blob_group)
                self.blob_groups.append(blob_group)

            elif match := re.search(Regex.BLOB_LINE, line):
                blob = Blob.from_regex_match(match=match, position=Position.from_int(cursor))
                cursor += len(blob)
                self.blobs.append(blob)

            elif match := re.search(Regex.MENU_STRING_LINE, line):
                string = String.from_regex_match(match=match, position=Position.from_int(cursor))
                cursor += len(string)
                self.blobs.append(string)

            elif match := re.search(Regex.FLAGS_LINE, line):
                flags = Flags.from_regex_match(match=match)

            elif match := re.search(Regex.LABEL_LINE, line):
                label = Label.from_regex_match(match=match, position=Position.from_int(cursor))
                cursor = int(label.position)
                self.labels.append(label)

            elif re.search(Regex.POINTER_LINE, line):
                lines_with_labels.append((line, cursor))
                cursor += 2

            elif match := re.search(Regex.BRANCHING_INSTRUCTION_LINE, line):
                command = match.group("command")

                if match.group("label"):
                    lines_with_labels.append((line, cursor))
                else:
                    instruction = BranchingInstruction.from_regex_match(match=match, position=Position.from_int(cursor))
                    self.branching_instructions.append(instruction)

                cursor += BranchingInstruction.find_length(command=command) + 1

            elif match := re.match(Regex.INSTRUCTION_LINE, line):
                instruction = Instruction.from_regex_match(match=match, position=Position.from_int(cursor), flags=flags)
                cursor += len(instruction)
                self.instructions.append(instruction)

                if instruction.is_flag_setter():
                    flags = instruction.set_flags(flags)

            elif not line.strip().startswith(";"):
                raise UnrecognizedLine(f"Line '{line}' is not recognized.")

        for line, cursor in lines_with_labels:
            if match := re.match(Regex.BRANCHING_INSTRUCTION_LINE, line):
                instruction = BranchingInstruction.from_regex_match(
                    match=match, position=Position.from_int(cursor), labels=self.labels
                )
                self.branching_instructions.append(instruction)

            elif match := re.match(Regex.POINTER_LINE, line):
                pointer = Pointer.from_regex_match(match=match, position=Position.from_int(cursor), labels=self.labels)
                self.pointers.append(pointer)

        for name in ["blobs", "blob_groups", "instructions", "branching_instructions", "pointers"]:
            _list = getattr(self, name)
            _list.sort()

    @classmethod
    def from_script_files(cls, *filenames: str | Path) -> Self:
        script = cls()
        for filename in filenames:
            script.append_script_file(filename)
        script.detect_conflicts()
        return script

    def detect_conflicts(self):
        self._sort_lists()
        # for label in self.labels:
        #      print(label)

        for i in range(len(self.labels) - 1):
            if self.labels[i].position == self.labels[i + 1].position:
                raise LabelConflict(
                    f"Labels '{self.labels[i].to_line()}' and '{self.labels[i + 1].to_line()}' point to the same address: {self.labels[i].position}"
                )

        lines = self.blobs + self.blob_groups + self.instructions + self.branching_instructions + self.pointers
        lines.sort()

        for i in range(len(lines) - 1):
            length = len(lines[i])
            if lines[i].position + length > lines[i + 1].position:
                raise LineConflict(
                    f"Lines '{lines[i].to_line(show_address=True)}' and '{lines[i + 1].to_line(show_address=True)}' are conflicting with one another."
                )

    def to_script_file(self, filename: str | Path, flags: Flags | None = None, debug: bool = False) -> None:
        self._extract_labels()
        lines = (
            self.labels
            + self.blobs
            + self.blob_groups
            + self.branching_instructions
            + self.instructions
            + self.pointers
        )
        lines.sort(key=lambda x: ScriptLine.sort(x))
        flags = flags or Flags()
        output = [flags.to_line()]

        cursor = int(lines[0].position)

        if not isinstance(lines[0], Label):
            start_label = Label(name="start", position=lines[0].position)
            self.labels.append(start_label)
            output.append(start_label.to_line(show_address=True))
            output.append(lines[0].to_line())
        else:
            output.append(lines[0].to_line(show_address=True))
        cursor += len(lines[0])

        for line in lines[1:]:
            if cursor != int(line.position):
                if isinstance(line, Label):
                    output.append(line.to_line(show_address=True))
                    cursor = int(line.position)
                    continue

                label = Label(position=line.position)
                self.labels.append(label)
                output.append(label.to_line(show_address=True))

            output.append(line.to_line(labels=self.labels, show_address=debug))
            cursor = int(line.position) + len(line)

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(output))

    def to_rom(self, output_path: str | Path, input_path: str | Path | None = None) -> None:
        input_path = input_path or output_path
        with open(input_path, "rb") as input_rom, open(output_path, "wb") as output_rom:
            rom = input_rom.read()
            output_rom.write(rom)
            for line in self.blobs + self.blob_groups + self.branching_instructions + self.instructions + self.pointers:
                output_rom.seek(int(line.position))
                output_rom.write(bytes(line))

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
                    cls._disassamble_instructions(cursor, f, script, section)

                elif section.mode in (ScriptMode.BLOBS, ScriptMode.MENU_STRINGS, ScriptMode.DESCRIPTION_STRINGS):
                    cls._disassemble_blobs(cursor, f, script, section)

                elif section.mode == ScriptMode.BLOB_GROUPS:
                    cls._disassemble_blob_groups(cursor, f, script, section)

        cls._sort_lists(script)

        return script

    @classmethod
    def _disassemble_blob_groups(cls, cursor: int, f: BinaryIO, script: Self, section: ScriptSection) -> None:
        if not section.attributes.get("sub_sections"):
            raise MissingSectionAttribute("Attribute 'sub_sections' is missing." f"Attributes: {section.attributes}")
        f.seek(cursor)
        while cursor < section.end:
            blob_group = BlobGroup(position=Position.from_int(cursor))

            for sub_section in section.attributes["sub_sections"]:
                data = cls._extract_blob_bytes(f=f, length=sub_section.length, delimiter=sub_section.delimiter)
                delimiter = sub_section.delimiter
                if sub_section.mode == ScriptMode.BLOBS:
                    blob = Blob(data=BEBytes.from_bytes(data), position=Position.from_int(cursor), delimiter=delimiter)
                elif sub_section.mode == ScriptMode.MENU_STRINGS:
                    blob = String(
                        data=BEBytes.from_bytes(data),
                        position=Position.from_int(cursor),
                        delimiter=delimiter,
                        string_type=StringTypes.MENU,
                    )
                elif sub_section.mode == ScriptMode.DESCRIPTION_STRINGS:
                    blob = String(
                        data=BEBytes.from_bytes(data),
                        position=Position.from_int(cursor),
                        delimiter=delimiter,
                        string_type=StringTypes.DESCRIPTION,
                    )
                else:
                    raise ValueError(f"Mode '{sub_section.mode}' unrecognized.")
                cursor += len(blob)
                blob_group.blobs.append(blob)
            script.blob_groups.append(blob_group)

    @classmethod
    def _disassemble_blobs(cls, cursor: int, f: BinaryIO, script: Self, section: ScriptSection) -> None:
        if section.attributes.get("length", None) is None and section.attributes.get("delimiter", None) is None:
            raise MissingSectionAttribute(
                "Attribute 'length' and 'delimiter' are missing. Please provide either of them."
                f"Attributes: {section.attributes}"
            )

        f.seek(cursor)
        delimiter = section.attributes.get("delimiter", None)
        while cursor < section.end:
            data = cls._extract_blob_bytes(
                f=f, length=section.attributes.get("length", None), delimiter=section.attributes.get("delimiter", None)
            )

            if data == b"":
                cursor += 1
                continue

            if section.mode == ScriptMode.BLOBS:
                blob = Blob.from_bytes(data=data, position=Position.from_int(cursor), delimiter=delimiter)
            elif section.mode == ScriptMode.MENU_STRINGS:
                blob = String.from_bytes(
                    data=data, position=Position.from_int(cursor), delimiter=delimiter, string_type=StringTypes.MENU
                )
            elif section.mode == ScriptMode.DESCRIPTION_STRINGS:
                blob = String.from_bytes(
                    data=data,
                    position=Position.from_int(cursor),
                    delimiter=delimiter,
                    string_type=StringTypes.DESCRIPTION,
                )
            script.blobs.append(blob)
            cursor += len(blob)

    @classmethod
    def _disassemble_pointers(cls, cursor: int, f: BinaryIO, script: Self, section: ScriptSection) -> None:
        while cursor < section.end:
            pointer_bytes = f.read(2)
            pointer = Pointer.from_bytes(position=Position.from_int(cursor), value=pointer_bytes)
            script.labels.append(Label(position=pointer.destination))
            script.pointers.append(pointer)
            cursor += 2

    @classmethod
    def _disassamble_instructions(cls, cursor: int, f: BinaryIO, script: Self, section: ScriptSection) -> None:
        if "flags" not in section.attributes:
            raise MissingSectionAttribute(f"Attribute 'flags' is missing. Attributes: {section.attributes}")
        flags = section.attributes["flags"]
        while cursor < section.end:
            f.seek(cursor)
            value = f.read(4)

            instruction = Instruction.from_bytes(position=Position.from_int(cursor), value=value, flags=flags)

            if isinstance(instruction, BranchingInstruction):
                script.branching_instructions.append(instruction)
                label = Label(position=instruction.destination)
                if label not in script.labels:
                    script.labels.append(label)
            else:
                if instruction.is_flag_setter():
                    flags = instruction.set_flags(flags)

                script.instructions.append(instruction)
            cursor += len(instruction)

    def _sort_lists(self) -> None:
        self.labels = sorted(self.labels)
        self.blobs.sort()
        self.blob_groups.sort()
        self.branching_instructions.sort()
        self.instructions.sort()
        self.pointers.sort()

    def _extract_labels(self) -> None:
        for script_line in self.pointers + self.branching_instructions:
            label = Label(position=script_line.destination)
            if label not in self.labels:
                self.labels.append(label)

    @staticmethod
    def _extract_blob_bytes(f: BinaryIO, length: int | None = None, delimiter: bytes | None = None) -> bytes:
        if length is not None:
            data = f.read(length)
        else:
            data = b""
            while (_char := f.read(1)) != bytes(delimiter):
                if _char == b"":
                    break
                data += _char
        return data


class UnrecognizedLine(Exception):
    pass
