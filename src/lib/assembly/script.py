from __future__ import annotations
import re
from enum import Enum, auto
from pathlib import Path
from typing import Self, BinaryIO, Any

from src.lib.assembly.artifact.variable import Label, SimpleVar
from src.lib.assembly.artifact.variables import Variables
from src.lib.misc.exception import MissingSectionAttribute, NoVariableException, LineConflict, UnrecognizedLine
from src.lib.assembly.data_structure.blob import Blob
from src.lib.assembly.data_structure.blob_group import BlobGroup
from src.lib.assembly.data_structure.pointer import Pointer
from src.lib.assembly.data_structure.instruction.instruction import Instruction
from src.lib.assembly.artifact.flags import Flags
from src.lib.assembly.data_structure.regex import Regex, InstructionRegex
from src.lib.assembly.data_structure.string.string import String, StringTypes
from src.lib.assembly.data_structure.data_structure import DataStructure
from src.lib.assembly.bytes import Bytes


class ScriptMode(Enum):
    """
    Script modes allows the disassembler to correctly interpret data it reads on the ROM.
    """

    INSTRUCTIONS = auto()
    POINTERS = auto()
    BLOBS = auto()
    MENU_STRINGS = auto()
    DESCRIPTION_STRINGS = auto()
    BLOB_GROUPS = auto()


class ScriptSection:
    """
    Script sections are used to define how to interpret a specific section of the ROM when disassembling.
    """

    def __init__(self, start: int, end: int, mode: ScriptMode, **attributes: Any):
        """
        :param start: The position of the beginning of the section.
        :param end: The position of the end of the section. The position itself is excluded from the section.
        :param mode: The script mode, used to allow the disassembler to properly interpret the data.
        :param attributes: The configs used to define the script section. They may differ according to the script
        section.
        """
        self.start = start
        self.end = end
        self.mode = mode
        self.attributes = attributes

    def __eq__(self, other: Self) -> bool:
        """
        :param other: The other script section.
        :return: Whether the two sections start at the same address.
        """
        return self.start == other.start

    def __lt__(self, other: Self) -> bool:
        """
        :param other: The other script section.
        :return: Whether the script section starts before the other one.
        """
        return self.start < other.start


class SubSection:
    """
    Subsections are used to define each individual subsection inside a blob group.
    """

    def __init__(self, mode: ScriptMode, length: int | None = None, delimiter: Bytes | None = None):
        """
        :param mode: The script mode of the subsection.
        :param length: An integer. If defined, will be used to determine the number of bytes shall be contained in the
        subsection.
        :param delimiter: A specific byte. If defined, will be used to determine the end of the blob.
        :raises MissingSectionAttribute: Raised when neither the length nor the delimiter is used.
        """
        if length is None and delimiter is None:
            raise MissingSectionAttribute("Please provide either the length or the delimiter.")
        self.mode = mode
        self.length = length
        self.delimiter = delimiter


class Script:
    """
    A script contains all the information necessary to either assemble into binary code or disassembly into a text file.
    """

    def __init__(self):
        self.blobs = list()
        self.blob_groups = list()
        self.instructions = list()
        self.pointers = list()
        self.variables = Variables()

    @classmethod
    def from_text_files(cls, *filenames: str | Path) -> Self:
        """
        Creates a script out of disassembled text files.
        :param filenames: The paths to the text files.
        :return: A script.
        """
        script = cls()
        for filename in filenames:
            script._append_script_file(filename)
        script._detect_conflicts()
        return script

    def _detect_conflicts(self):
        """
        Checks if any data structure position conflicts with another.
        :return: None.
        :raises LineConflict: Raised when a line overlaps with the next one, when sorted by position.
        """
        lines = self.blobs + self.blob_groups + self.instructions + self.pointers
        lines.sort()

        for i in range(len(lines) - 1):
            length = len(lines[i])
            if lines[i].position + length > lines[i + 1].position:
                raise LineConflict(
                    f"Lines '{lines[i].to_line(show_address=True)}' and '{lines[i + 1].to_line(show_address=True)}' are conflicting with one another."
                )

    def to_text_file(self, filename: str | Path, flags: Flags | None = None, debug: bool = False) -> None:
        """
        Disassembles a script into a text file.
        :param filename: The path of the text file.
        :param flags: The Flags object to determine the initial states of the 'm' and 'x' flags.
        :param debug: When True, will append line position as a comment to any line that doesn't already display it.
        :return: None.
        """
        self._extract_labels()
        lines = self.variables.labels + self.blobs + self.blob_groups + self.instructions + self.pointers
        lines.sort(key=lambda x: DataStructure.sort(x))
        flags = flags or Flags()
        output = [flags.to_line(), ""]
        for simple_variable in self.variables.simple_variables:
            output.append(f"{simple_variable.to_line()}")

        cursor = int(lines[0].position)
        current_anchor = Bytes.from_int(0)

        if not isinstance(lines[0], Label):
            start_label = Label(name="start", value=lines[0].position)
            self.variables.append(start_label)
            output.append(start_label.to_line(show_address=True))
            output.append(lines[0].to_line())
        else:
            output.append(lines[0].to_line(show_address=True))
        cursor += len(lines[0])

        for line in lines[1:]:
            if cursor != int(line.position):
                if isinstance(line, Label):
                    output.append(line.to_line(show_address=True))
                    cursor = int(line.value)
                    continue

                label = Label(value=line.position)
                self.variables.append(label)
                output.append(label.to_line(show_address=True))

            if isinstance(line, Pointer) and line.is_relative:
                output.append(
                    line.to_line(labels=self.variables.labels, show_address=debug, current_anchor=current_anchor)
                )
                current_anchor = line.anchor
            else:
                output.append(line.to_line(labels=self.variables.labels, show_address=debug))
            cursor = int(line.position) + len(line)

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(output))

    def to_rom(self, output_path: str | Path, input_path: str | Path | None = None) -> None:
        """
        Assembles a script into a ROM using a source ROM to modify.
        :param output_path: The destination ROM path.
        :param input_path: The source ROM path.
        :return: None.
        """
        input_path = input_path or output_path
        with open(input_path, "rb") as input_rom, open(output_path, "wb") as output_rom:
            rom = input_rom.read()
            output_rom.write(rom)
            for line in self.blobs + self.blob_groups + self.instructions + self.pointers:
                output_rom.seek(int(line.position))
                output_rom.write(bytes(line))

    @classmethod
    def from_rom(cls, filename: str | Path, sections: list[ScriptSection]) -> Self:
        """
        Disassembles a ROM into a script.
        :param filename: The path of the ROM.
        :param sections: A list of sections to interpret the ROM data.
        :return: A script.
        """
        script = cls()
        with open(filename, "rb") as f:
            for section in sections:
                cursor = section.start
                f.seek(cursor)

                if section.mode == ScriptMode.POINTERS:
                    cls._disassemble_pointers(cursor, f, script, section)

                elif section.mode == ScriptMode.INSTRUCTIONS:
                    cls._disassemble_instructions(cursor, f, script, section)

                elif section.mode in (ScriptMode.BLOBS, ScriptMode.MENU_STRINGS, ScriptMode.DESCRIPTION_STRINGS):
                    cls._disassemble_blobs(cursor, f, script, section)

                elif section.mode == ScriptMode.BLOB_GROUPS:
                    cls._disassemble_blob_groups(cursor, f, script, section)

        cls._sort_lists(script)

        return script

    def _append_script_file(self, filename: str | Path) -> None:
        """
        Parses a text file to add to an existing script.
        :param filename: The path of the text file.
        :return: None.
        """
        with open(filename, encoding="utf-8") as f:
            lines = f.readlines()
        lines = [stripped_line for line in lines if (stripped_line := line.rstrip())]

        cursor = 0
        flags = Flags()
        lines_with_labels = list()
        anchor = None

        for line in lines:
            cursor, flags = self._interpret_line(cursor, flags, line, lines_with_labels)

        for line, cursor, flags in lines_with_labels:
            if match := re.match(InstructionRegex.INSTRUCTION, line):
                instruction = Instruction.from_match(
                    match=match, position=Bytes.from_position(cursor), variables=self.variables, flags=flags
                )
                self.instructions.append(instruction)
            elif match := re.match(Regex.ANCHOR, line):
                anchor = Bytes.from_anchor_match(value=match, labels=self.variables.labels)

            elif match := re.match(Regex.POINTER_LINE, line):
                pointer = Pointer.from_match(
                    match=match, position=Bytes.from_position(cursor), labels=self.variables.labels, anchor=anchor
                )
                self.pointers.append(pointer)

        for name in ["blobs", "blob_groups", "instructions", "pointers"]:
            _list = getattr(self, name)
            _list.sort()

    def _interpret_line(
        self, cursor: int, flags: Flags, line: str, lines_with_labels: list[tuple[str, int, Flags]]
    ) -> tuple[int, Flags]:
        """
        Parse a line in a text file.
        :param cursor: The current position of the line being parsed.
        :param flags: A Flags object to determine the state of the 'm' and the 'x' flags.
        :param line: The line being parsed.
        :param lines_with_labels: A list of lines with additional info to be parsed later.
        :return: A tuple of the new cursor position and flags state.
        """
        if re.match(Regex.ANCHOR, line):
            lines_with_labels.append((line, cursor, flags))

        elif match := re.fullmatch(Regex.VARIABLE_ASSIGNMENT, line):
            self.variables.append(SimpleVar.from_match(match))

        elif match := re.match(Regex.DESCRIPTION_LINE, line):
            string = String.from_match(match=match, position=Bytes.from_position(cursor))
            cursor += len(string)
            self.blobs.append(string)

        elif match := re.fullmatch(Regex.BLOB_GROUP_LINE, line):
            blob_group = BlobGroup.from_match(match=match, position=Bytes.from_position(cursor))
            cursor += len(blob_group)
            self.blob_groups.append(blob_group)

        elif match := re.search(Regex.BLOB_LINE, line):
            blob = Blob.from_match(match=match, position=Bytes.from_position(cursor))
            cursor += len(blob)
            self.blobs.append(blob)

        elif match := re.search(Regex.MENU_STRING_LINE, line):
            string = String.from_match(match=match, position=Bytes.from_position(cursor))
            cursor += len(string)
            self.blobs.append(string)

        elif match := re.search(Regex.FLAGS_LINE, line):
            flags = Flags.from_match(match=match)

        elif match := re.search(Regex.LABEL_LINE, line):
            label = Label.from_match(match=match, position=Bytes.from_position(cursor))
            cursor = int(label.value)
            self.variables.append(label)

        elif re.search(Regex.POINTER_LINE, line):
            lines_with_labels.append((line, cursor, flags))
            cursor += 2

        elif match := re.match(InstructionRegex.INSTRUCTION, line):
            try:
                instruction = Instruction.from_match(
                    match=match, position=Bytes.from_position(cursor), flags=flags, variables=self.variables
                )
            except NoVariableException:
                lines_with_labels.append((line, cursor, flags))
                prefixes = re.findall(r"[.!]", line)
                cursor += Instruction.find_length(match.group("command"), prefixes[0] if prefixes else None)
            else:
                cursor += len(instruction)
                self.instructions.append(instruction)

                if instruction.is_flag_setter():
                    flags = instruction.set_flags(flags)

                for operand in instruction.operands:
                    if operand.variable and operand.variable not in self.variables:
                        self.variables.append(operand.variable)

        elif not line.strip().startswith(";"):
            raise UnrecognizedLine(f"Line '{line}' is not recognized.")

        return cursor, flags

    @classmethod
    def _disassemble_blob_groups(cls, cursor: int, f: BinaryIO, script: Self, section: ScriptSection) -> None:
        """
        Disassembles a blob group section.
        :param cursor: The current position being read in the ROM.
        :param f: The stream being currently opened which is reading the ROM.
        :param script: The script being created.
        :param section: The blob group section info.
        :return: None.
        :raises MissingSectionAttribute: Raised when the section misses the 'subsections' attribute.
        """
        if not section.attributes.get("sub_sections"):
            raise MissingSectionAttribute("Attribute 'sub_sections' is missing." f"Attributes: {section.attributes}")
        f.seek(cursor)
        while cursor < section.end:
            blob_group = BlobGroup(position=Bytes.from_position(cursor))

            for sub_section in section.attributes["sub_sections"]:
                data = cls._extract_blob_bytes(f=f, length=sub_section.length, delimiter=sub_section.delimiter)
                delimiter = sub_section.delimiter
                if sub_section.mode == ScriptMode.BLOBS:
                    blob = Blob(data=Bytes.from_bytes(data), position=Bytes.from_position(cursor), delimiter=delimiter)
                elif sub_section.mode == ScriptMode.MENU_STRINGS:
                    blob = String(
                        data=Bytes.from_bytes(data),
                        position=Bytes.from_position(cursor),
                        delimiter=delimiter,
                        string_type=StringTypes.MENU,
                    )
                elif sub_section.mode == ScriptMode.DESCRIPTION_STRINGS:
                    blob = String(
                        data=Bytes.from_bytes(data),
                        position=Bytes.from_position(cursor),
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
        """
        Disassembles a blob section.
        :param cursor: The current position being read in the ROM.
        :param f: The stream being currently opened which is reading the ROM.
        :param script: The script being created.
        :param section: The blob section info.
        :return: None.
        :raises MissingSectionAttribute: Raised when the section misses both the 'length' and 'delimiter' attributes.
        """
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
                blob = Blob.from_bytes(data=data, position=Bytes.from_position(cursor), delimiter=delimiter)
            elif section.mode == ScriptMode.MENU_STRINGS:
                blob = String.from_bytes(
                    data=data, position=Bytes.from_position(cursor), delimiter=delimiter, string_type=StringTypes.MENU
                )
            else:  # section.mode == ScriptMode.DESCRIPTION_STRINGS
                blob = String.from_bytes(
                    data=data,
                    position=Bytes.from_int(cursor),
                    delimiter=delimiter,
                    string_type=StringTypes.DESCRIPTION,
                )

            script.blobs.append(blob)
            cursor += len(blob)

    @classmethod
    def _disassemble_pointers(cls, cursor: int, f: BinaryIO, script: Self, section: ScriptSection) -> None:
        """
        Disassembles a pointer section.
        :param cursor: The current position being read in the ROM.
        :param f: The stream being currently opened which is reading the ROM.
        :param script: The script being created.
        :param section: The pointer info.
        :return: None.
        """
        anchor = None

        if position := section.attributes.get("anchor", 0):
            anchor = Bytes.from_position(position)
            script.variables.append(Label(value=anchor))

        while cursor < section.end:
            pointer_bytes = f.read(2)
            pointer = Pointer.from_bytes(position=Bytes.from_position(cursor), value=pointer_bytes, anchor=anchor)
            script.variables.append(Label(value=pointer.destination))
            script.pointers.append(pointer)
            cursor += 2

    @classmethod
    def _disassemble_instructions(cls, cursor: int, f: BinaryIO, script: Self, section: ScriptSection) -> None:
        """
        Disassembles an instruction section.
        :param cursor: The current position being read in the ROM.
        :param f: The stream being currently opened which is reading the ROM.
        :param script: The script being created.
        :param section: The instruction section info.
        :return: None.
        :raises MissingSectionAttribute: Raised when the section misses the 'flags' attribute.
        """
        if "flags" not in section.attributes:
            raise MissingSectionAttribute(f"Attribute 'flags' is missing. Attributes: {section.attributes}")
        flags = section.attributes["flags"]
        while cursor < section.end:
            f.seek(cursor)
            value = f.read(4)

            instruction = Instruction.from_bytes(
                position=Bytes.from_position(cursor), value=value, flags=flags, variables=script.variables
            )

            if instruction.is_flag_setter():
                flags = instruction.set_flags(flags)
            elif instruction.has_destination():
                script.variables.append(instruction.operands[0].variable)

            script.instructions.append(instruction)
            cursor += len(instruction)

    def _sort_lists(self) -> None:
        """
        Sorts all lists contained in the script.
        :return: None.
        """
        self.variables.sort()
        self.blobs.sort()
        self.blob_groups.sort()
        self.instructions.sort()
        self.pointers.sort()

    def _extract_labels(self) -> None:
        """
        Extracts all labels from pointers and instructions.
        :return: None.
        """
        for script_line in self.pointers:
            label = Label(value=script_line.destination)
            if not self.variables.find_by_position(label.position):
                self.variables.append(label)
        for script_line in self.instructions:
            if script_line.has_destination():
                label = script_line.operands[0].variable
                if not self.variables.find_by_position(label.position):
                    self.variables.append(label)

    @staticmethod
    def _extract_blob_bytes(f: BinaryIO, length: int | None = None, delimiter: bytes | None = None) -> bytes:
        """
        Extract the bytes of the blob.
        :param f: The stream being currently opened which is reading the ROM.
        :param length: The length of the blob.
        :param delimiter: The byte used to determine the end of the blob.
        :return: The blob as a bytes array.
        """
        if length is not None:
            return f.read(length)

        data = b""
        while (_char := f.read(1)) != bytes(delimiter):
            if _char == b"":
                break
            data += _char
        return data
