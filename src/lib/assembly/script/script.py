from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Self, BinaryIO

from src.lib.assembly.artifact.variable import Label, SimpleVar
from src.lib.assembly.artifact.variables import Variables
from src.lib.assembly.data_structure.instruction.operand import Operand
from src.lib.assembly.script.helpers import ScriptMode, ScriptSection, Line, LineType, clean_line, Component
from src.lib.misc.exception import (
    MissingSectionAttribute,
    LineConflict,
    UnrecognizedLine,
    UnrecognizedSubsectionMode,
    UndefinedFlags,
)
from src.lib.assembly.data_structure.blob import Blob
from src.lib.assembly.data_structure.array import Array
from src.lib.assembly.data_structure.pointer import Pointer
from src.lib.assembly.data_structure.instruction.instruction import Instruction
from src.lib.assembly.artifact.flags import Flags, RegisterWidth
from src.lib.assembly.data_structure.regex import InstructionRegex, ArtifactRegex, DataStructureRegex
from src.lib.assembly.data_structure.string.string import String, StringTypes
from src.lib.assembly.data_structure.data_structure import DataStructure
from src.lib.assembly.bytes import Bytes


class Script:
    """
    A script contains all the information necessary to either assemble into binary code or disassembly into a text file.
    """

    def __init__(self):
        self.lines = list()

    @classmethod
    def parse(cls, *filenames: str | Path) -> Self:
        """
        Creates a script out of disassembled text files.
        :param filenames: The paths to the text files.
        :return: A Script.
        """
        logging.info(f"Parsing script files: {filenames}.")
        script = cls()
        for filename in filenames:
            script.lines += cls._append_script_file(filename)

        cursor = 0
        for line in script.lines:
            logging.debug(f"Pre-parsing {repr(line)}.")
            cursor = script._preparse_line(line, cursor)
        script._parse_lines()

        script._detect_conflicts()
        return script

    def _detect_conflicts(self):
        """
        Checks if any data structure position conflicts with another.
        :return: None.
        :raises LineConflict: Raised when a line overlaps with the next one, when sorted by position.
        """
        self._sort_lines()
        data_lines = [line for line in self.lines if line.component and line.component_info != LineType.LABEL]

        for i, line in enumerate(data_lines[:-1]):
            length = len(line.component)
            if line.position + length > data_lines[i + 1].position:
                message = f"Conflicting lines: '{repr(line)}' and " f"'{repr(data_lines[i + 1])}'."
                logging.error(message)
                raise LineConflict(message)

        flag_lines = [line for line in self.lines if line.component and line.component_info == LineType.FLAGS]
        for i, line in enumerate(flag_lines[:-1]):
            if line.position == flag_lines[i + 1].position and line.component != flag_lines[i + 1].component:
                message = (
                    f"Flags lines {repr(line)} and {repr(flag_lines[i + 1])} "
                    f"at position 0x{str(line.component.position)} are conflicting with one another."
                )
                logging.error(message)
                raise LineConflict(message)

    def dump(self, filename: str | Path, debug: bool = False) -> None:
        """
        Dumps a script into a text file.
        :param filename: The path of the text file.
        :param debug: When True, will append line position as a comment to any line that doesn't already display it.
        :return: None.
        """
        logging.info(f"Dumping script to file '{filename}'.")
        self._extract_labels()
        self._sort_lines()
        output = []

        cursor = 0
        current_anchor = Operand(Bytes.from_int(0))

        first_component = self.data_structures()[0]
        flags = Flags(m=RegisterWidth.INVALID, x=RegisterWidth.INVALID)

        if not self.labels().find_by_position(first_component.position):
            name = "start" if not self.labels().find_by_name("start") else None
            start_label = Label(name=name, value=first_component.position)
            logging.info(f"Added {repr(start_label)}.")
            self.lines.append(Line.from_component(start_label))
            self._sort_lines()

        for component in self.components():
            logging.info(f"Dumping {repr(component)}.")
            if flags and isinstance(component, Flags):
                if flags.m == component.m and flags.x == component.x:
                    logging.debug("Unnecessary flags redifinition. Skipping.")
                    continue
                flags = component
            if cursor != int(component.position):
                if isinstance(component, Label):
                    output.append(component.to_line(show_address=True))
                    logging.debug(f"Setting cursor at 0x{Bytes.from_position(cursor)}.")
                    cursor = int(component.value)
                    continue

                label = Label(value=component.position)
                logging.info(f"Created {repr(label)}.")
                self.lines.append(Line.from_component(label))
                logging.info(f"Writing {repr(label)} to file.")
                output.append(label.to_line(show_address=True))

            if isinstance(component, Instruction) and component.is_flag_setter():
                flags = component.set_flags(flags)

            if isinstance(component, Pointer) and component.is_relative:
                output.append(
                    component.to_line(labels=self.labels(), show_address=debug, current_anchor=current_anchor)
                )
                current_anchor = component.anchor
            else:
                output.append(component.to_line(labels=self.labels(), show_address=debug))
            cursor = int(component.position) + len(component)
            logging.debug(f"Advancing cursor to 0x{Bytes.from_position(cursor)}.")

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(output))

    def assemble(self, output_path: str | Path, input_path: str | Path | None = None) -> None:
        """
        Assembles a script into a ROM using a source ROM to modify.
        :param output_path: The destination ROM path.
        :param input_path: The source ROM path.
        :return: None.
        """
        logging.info(f"Assembling to ROM '{output_path}'.")
        input_path = input_path or output_path
        with open(input_path, "rb") as input_rom, open(output_path, "wb") as output_rom:
            rom = input_rom.read()
            output_rom.write(rom)
            for line in self.data_structures():
                logging.info(f"Assembling {repr(line)} to ROM.")
                output_rom.seek(int(line.position))
                output_rom.write(bytes(line))

    @classmethod
    def disassemble(cls, filename: str | Path, sections: list[ScriptSection]) -> Self:
        """
        Disassembles a ROM into a script.
        :param filename: The path of the ROM.
        :param sections: A list of sections to interpret the ROM data.
        :return: A script.
        """
        logging.info(f"Disassembling from ROM '{filename}'.")
        script = cls()
        with open(filename, "rb") as f:
            for section in sections:
                logging.info(f"Disassembling {section.mode} section starting at {Bytes.from_position(section.start)}.")

                cursor = section.start
                f.seek(cursor)

                if section.mode == ScriptMode.POINTERS:
                    cls._disassemble_pointers(cursor, f, script, section)

                elif section.mode == ScriptMode.INSTRUCTIONS:
                    cls._disassemble_instructions(cursor, f, script, section)

                elif section.mode in (ScriptMode.BLOBS, ScriptMode.MENU_STRINGS, ScriptMode.MENU_DESCRIPTIONS):
                    cls._disassemble_blobs(cursor, f, script, section)

                elif section.mode == ScriptMode.ARRAYS:
                    cls._disassemble_arrays(cursor, f, script, section)

        cls._sort_lines(script)

        return script

    def _sort_lines(self) -> None:
        """
        Sorts the script lines by position, with Flags and Labels in priority.
        :return: Nothing.
        """
        self.lines.sort(key=lambda x: x.component_info != LineType.FLAGS)
        self.lines.sort(key=lambda x: x.component_info != LineType.LABEL)
        self.lines.sort(key=lambda x: x.position)

    @classmethod
    def _append_script_file(cls, filename: str | Path) -> list[Line]:
        """
        Parses a text file and return Lines.
        :param filename: The path of the text file.
        :return: A list of Lines.
        """
        lines = list()

        logging.info(f"Appending file '{filename}'.")

        with open(filename, encoding="utf-8") as f:
            for raw_string in f.readlines():
                if clean_string := clean_line(raw_string):
                    lines.append(Line(filename, raw_string, clean_string))

        lines[0].position = 0
        return lines

    def _parse_lines(self) -> None:
        """
        Parses the script line and finishes filling the Line fields.
        :return: Nothing.
        :raises UnrecognizedLine: Raised when the Component type can't be determined.
        """
        flags = Flags(m=RegisterWidth.INVALID, x=RegisterWidth.INVALID)
        anchor = None

        for line in self.lines:
            logging.info(f"Parsing {repr(line)}.")
            position = Bytes.from_position(line.position)

            if line.component_info in (LineType.VARIABLE_DECLARATION, LineType.LABEL):
                continue

            if line.component_info == LineType.ANCHOR:
                anchor = Operand.from_line(**line.regex_groups, parent_position=position, variables=self.variables())
                logging.info(f"New anchor: {repr(anchor)}.")
            elif line.component_info == LineType.ARRAY:
                array = Array.from_line(line=line.clean_line, position=position, variables=self.simple_vars())
                line.component = array
            elif line.component_info == LineType.BLOB:
                blob = Blob.from_line(**line.regex_groups, position=position, variables=self.simple_vars())
                line.component = blob
            elif line.component_info == LineType.FLAGS:
                new_flags = Flags.from_line(**line.regex_groups, position=position)
                if new_flags != flags:
                    logging.info(f"New flags have been detected. {repr(new_flags)}")
                flags = new_flags
                line.component = Flags.copy(new_flags)
            elif line.component_info == LineType.INSTRUCTION:
                if flags.m == RegisterWidth.INVALID or flags.x == RegisterWidth.INVALID:
                    message = "Flags have not been defined before the first instruction."
                    logging.error(message)
                    raise UndefinedFlags(message)
                instruction = Instruction.from_line(
                    **line.regex_groups, flags=flags, position=position, variables=self.variables()
                )
                if instruction.is_flag_setter():
                    flags = instruction.set_flags(flags)
                    logging.info(f"Instruction is a flag setter. New flags: {repr(flags)}.")
                line.component = instruction
            elif line.component_info == LineType.POINTER:
                pointer = Pointer.from_line(**line.regex_groups, position=position, anchor=anchor, labels=self.labels())
                line.component = pointer
            elif line.component_info == LineType.STRING:
                string = String.from_line(**line.regex_groups, position=position, variables=self.simple_vars())
                line.component = string
            elif line.component_info == LineType.VARIABLE_DECLARATION:
                continue
            else:
                raw_line = line.raw_line.strip("\n")
                message = f"Line '{raw_line}' in file '{line.filename}' is not recognized."
                logging.error(message)
                raise UnrecognizedLine(message)

    def _preparse_line(
        self,
        line: Line,
        cursor: int,
    ) -> int:
        """
        Prepares the parsing of a script line by filling some of the fields of the Line and determining the Line length.
        :param line: The line being parsed as a string or as the Line object containing it.
        :param cursor: The current position of the line being parsed. Will be overridden if the line has a position
        because this is the first line of a new file.
        :return: The new position of the cursor.
        """

        if line.position is not None:
            cursor = line.position

        cleaned_line = line.clean_line if isinstance(line, Line) else line

        if match := re.fullmatch(ArtifactRegex.VARIABLE_DECLARATION, cleaned_line):
            line.component = SimpleVar.from_line(
                length=match.group("length"), name=match.group("name"), operand=match.group("operand")
            )
            line.component_info = LineType.VARIABLE_DECLARATION
            line.position = 0

        if isinstance(line, Line):
            line.position = cursor

        if match := re.fullmatch(ArtifactRegex.LABEL, cleaned_line):
            label = Label.from_line(
                name=match.group("name"), snes_address=match.group("snes_address"), position=Bytes.from_position(cursor)
            )
            cursor = int(label.value)
            logging.debug(f"Cursor set at 0x{Bytes.from_position(cursor)}.")
            line.component_info = LineType.LABEL
            line.component = label
            line.position = cursor

        elif match := re.fullmatch(ArtifactRegex.ANCHOR, cleaned_line):
            line.component_info = LineType.ANCHOR

        elif match := re.fullmatch(ArtifactRegex.FLAGS, cleaned_line):
            line.component_info = LineType.FLAGS

        elif re.fullmatch(DataStructureRegex.ARRAY, cleaned_line):
            cursor += Array.find_length(cleaned_line, self.variables())
            line.component_info = LineType.ARRAY

        elif match := re.fullmatch(DataStructureRegex.POINTER, cleaned_line):
            cursor += Pointer.find_length()
            line.component_info = LineType.POINTER

        elif match := re.fullmatch(DataStructureRegex.BLOB, cleaned_line):
            cursor += Blob.find_length(
                operand=match.group("operand"), variables=self.simple_vars(), delimiter=match.group("delimiter")
            )
            line.component_info = LineType.BLOB

        elif match := re.fullmatch(DataStructureRegex.STRING, cleaned_line):
            cursor += String.find_length(string=match.group("string"), delimiter=match.group("delimiter"))
            line.component_info = LineType.STRING

        elif match := re.match(InstructionRegex.INSTRUCTION, cleaned_line):
            cursor += Instruction.find_length(
                command=match.group("command"), operand=match.group("operand"), variables=self.variables()
            )
            line.component_info = LineType.INSTRUCTION

        if isinstance(line, Line):
            if match:
                line.regex_groups = {
                    group: match.group(group) if line.component_info.regex_groups else None
                    for group in line.component_info.regex_groups
                }

        return cursor

    @classmethod
    def _disassemble_arrays(cls, cursor: int, f: BinaryIO, script: Self, section: ScriptSection) -> None:
        """
        Disassembles an Array section.
        :param cursor: The current position being read in the ROM.
        :param f: The stream being currently opened which is reading the ROM.
        :param script: The script being created.
        :param section: The blob group section info.
        :return: None.
        :raises MissingSectionAttribute: Raised when the section misses the 'subsections' attribute.
        """
        if not section.attributes.get("sub_sections"):
            message = "Attribute 'sub_sections' is missing." f"Attributes: {section.attributes}"
            logging.error(message)
            raise MissingSectionAttribute(message)

        f.seek(cursor)
        while cursor < section.end:
            array = Array(position=Bytes.from_position(cursor))

            for sub_section in section.attributes["sub_sections"]:
                data = cls._extract_blob_bytes(f=f, length=sub_section.length, delimiter=sub_section.delimiter)
                delimiter = sub_section.delimiter
                if sub_section.mode == ScriptMode.BLOBS:
                    blob = Blob.from_bytes(data=data, position=Bytes.from_position(cursor), delimiter=delimiter)
                elif sub_section.mode == ScriptMode.MENU_STRINGS:
                    blob = String.from_bytes(
                        data=data,
                        position=Bytes.from_position(cursor),
                        delimiter=delimiter,
                        string_type=StringTypes.MENU,
                    )
                elif sub_section.mode == ScriptMode.MENU_DESCRIPTIONS:
                    blob = String.from_bytes(
                        data=data,
                        position=Bytes.from_position(cursor),
                        delimiter=delimiter,
                        string_type=StringTypes.DESCRIPTION,
                    )
                else:
                    message = f"Mode '{sub_section.mode}' unrecognized."
                    logging.error(message)
                    raise UnrecognizedSubsectionMode(message)

                cursor += len(blob)
                array.parts.append(blob)
            script.lines.append(Line.from_component(array))

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
            message = (
                "Attribute 'length' and 'delimiter' are missing. Please provide either of them."
                f"Attributes: {section.attributes}"
            )
            logging.error(message)
            raise MissingSectionAttribute(message)

        f.seek(cursor)
        delimiter = section.attributes.get("delimiter", None)
        if delimiter is not None:
            pass
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
                    position=Bytes.from_position(cursor),
                    delimiter=delimiter,
                    string_type=StringTypes.DESCRIPTION,
                )

            script.lines.append(Line.from_component(blob))
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
            anchor = Operand(Bytes.from_position(position))
            label = Label(value=anchor.value)
            if not script.labels().find_by_position(label.position):
                script.lines.append(Line.from_component(label))

        while cursor < section.end:
            pointer_bytes = f.read(2)
            pointer = Pointer.from_bytes(position=Bytes.from_position(cursor), value=pointer_bytes, anchor=anchor)
            label = Label(value=pointer.destination)
            if not script.labels().find_by_position(label.position):
                script.lines.append(Line.from_component(label))
            script.lines.append(Line.from_component(pointer))
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
            message = f"Attribute 'flags' is missing. Attributes: {section.attributes}"
            logging.error(message)
            raise MissingSectionAttribute(message)

        flags = section.attributes["flags"]
        script.lines.append(
            Line.from_component(Flags(m=flags.m, x=flags.x, position=Bytes.from_position(section.start)))
        )
        while cursor < section.end:
            f.seek(cursor)
            value = f.read(4)

            instruction = Instruction.from_bytes(
                position=Bytes.from_position(cursor), value=value, flags=flags, variables=script.variables()
            )

            if instruction.is_flag_setter():
                flags = instruction.set_flags(flags)
            elif instruction.labels:
                for label in instruction.labels:
                    if not script.labels().find_by_position(label.position):
                        script.lines.append(Line.from_component(label))

            script.lines.append(Line.from_component(instruction))
            cursor += len(instruction)

    def _extract_labels(self) -> None:
        """
        Extracts all labels from pointers and instructions.
        :return: None.
        """
        for pointer in self.pointers():
            if pointer.operand.variable:
                label = pointer.operand.variable
                if not self.variables().find_by_position(label.position):
                    self.lines.append(Line.from_component(label))
        for instruction in self.instructions():
            for label in instruction.labels:
                if not self.variables().find_by_position(label.position):
                    self.lines.append(Line.from_component(label))

    @staticmethod
    def _extract_blob_bytes(f: BinaryIO, length: int | None = None, delimiter: bytes | None = None) -> bytes:
        """
        Extracts the bytes of a blob.
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

    def variables(self) -> Variables:
        return Variables(*self._get_components(LineType.VARIABLE_DECLARATION, LineType.LABEL))

    def simple_vars(self):
        return Variables(*self._get_components(LineType.VARIABLE_DECLARATION))

    def labels(self):
        return Variables(*self._get_components(LineType.LABEL))

    def flags(self):
        return self._get_components(LineType.FLAGS)

    def pointers(self):
        return self._get_components(LineType.POINTER)

    def instructions(self):
        return self._get_components(LineType.INSTRUCTION)

    def blobs(self):
        return self._get_components(LineType.BLOB)

    def strings(self):
        return self._get_components(LineType.STRING)

    def arrays(self):
        return self._get_components(LineType.ARRAY)

    def components(self) -> list[Component]:
        return [line.component for line in self.lines if line.component]

    def data_structures(self) -> list[DataStructure]:
        return [line.component for line in self.lines if isinstance(line.component, DataStructure)]

    def _get_components(self, *component_infos: LineType) -> list[Component]:
        """
        Obtains the Components inside the Lines.
        :param component_infos: If provided, will filter the results by Component type.
        :return: A list of Components.
        """
        return [line.component for line in self.lines if line.component_info in component_infos]
