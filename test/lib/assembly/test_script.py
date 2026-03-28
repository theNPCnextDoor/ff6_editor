from pathlib import Path

import pytest

from src.lib.assembly.artifact.variables import Variables
from src.lib.assembly.data_structure.blob import Blob
from src.lib.assembly.data_structure.blob_group import BlobGroup
from src.lib.assembly.data_structure.instruction.operand import Operand, OperandType
from src.lib.assembly.data_structure.string.string import String, StringTypes
from src.lib.assembly.bytes import Bytes, Endian
from src.lib.assembly.artifact.flags import Flags
from src.lib.assembly.data_structure.instruction.instruction import Instruction
from src.lib.assembly.artifact.variable import Label
from src.lib.assembly.data_structure.pointer import Pointer
from src.lib.assembly.script import (
    Script,
    ScriptMode,
    ScriptSection,
    SubSection,
)
from src.lib.misc.exception import LineConflict, UnrecognizedLine
from src.lib.assembly.data_structure.string.charset import MENU_CHARSET, Charset
from test import RESOURCES_FOLDER
from test.lib.assembly.conftest import TEST_BYTE, TEST_WORD, TEST_POSITION, ALFA, BRAVO

CONFLICTING_FILE_1 = Path(RESOURCES_FOLDER, "conflicting_file_1.asm")
CONFLICTING_FILE_2 = Path(RESOURCES_FOLDER, "conflicting_file_2.asm")
CONFLICTING_LABELS_SCRIPT = Path(RESOURCES_FOLDER, "conflicting_labels_script.asm")
CONFLICTING_LINES_SCRIPT = Path(RESOURCES_FOLDER, "conflicting_lines_script.asm")
DUMMY_INPUT_SCRIPT_1 = Path(RESOURCES_FOLDER, "dummy_input_script_1.asm")
DUMMY_INPUT_SCRIPT_2 = Path(RESOURCES_FOLDER, "dummy_input_script_2.asm")
DUMMY_ERROR_SCRIPT = Path(RESOURCES_FOLDER, "dummy_error_script.asm")
DUMMY_OUTPUT_SCRIPT = Path(RESOURCES_FOLDER, "dummy_output_script.asm")
DUMMY_INPUT_ROM = Path(RESOURCES_FOLDER, "dummy_input_rom.sfc")
DUMMY_OUTPUT_ROM = Path(RESOURCES_FOLDER, "dummy_output_rom.sfc")


class ScriptImpl:
    def __init__(self):
        self.script = Script()

        self.script.flags = Flags()

        self.script.variables = Variables(
            ALFA,
            BRAVO,
            Label(value=Bytes([0x00, 0x00, 0x01]), name="start"),
            Label(value=Bytes([0x00, 0x00, 0x05]), name="archie"),
            Label(value=Bytes([0x12, 0x00, 0x01]), name="anchor_1"),
            Label(value=Bytes([0x00, 0xFE, 0xDC]), name="label_c0fedc"),
        )

        self.script.pointers = [
            Pointer(position=Bytes([0x00, 0x00, 0x01]), destination=Bytes([0x00, 0x12, 0x34])),
            Pointer(position=Bytes([0x00, 0x00, 0x03]), destination=Bytes([0x00, 0x00, 0x05])),
        ]

        self.script.instructions = [
            Instruction(position=Bytes([0x00, 0x00, 0x05]), opcode=Bytes([0xAA]), operands=None),
            Instruction(
                position=Bytes([0x00, 0x00, 0x06]),
                opcode=Bytes([0xA1]),
                operands=[Operand(TEST_BYTE, "(_,X)", variable=ALFA)],
            ),
            Instruction(
                position=Bytes([0x00, 0x00, 0x08]), opcode=Bytes([0xA2]), operands=[Operand(Bytes([0xFE, 0xDC]), "#_")]
            ),
            Instruction(
                position=Bytes([0x00, 0x00, 0x0B]), opcode=Bytes([0xC2]), operands=[Operand(Bytes([0x30]), "#_")]
            ),
            Instruction(
                position=Bytes([0x00, 0x00, 0x0D]),
                opcode=Bytes([0xA9]),
                operands=[Operand(Bytes([0x12, 0x34]), "#_", variable=BRAVO)],
            ),
            Instruction(
                position=Bytes([0x00, 0x00, 0x10]),
                opcode=Bytes([0xA2]),
                operands=[
                    Operand(
                        Bytes([0xFE, 0xDC]), "#_", variable=Label(value=Bytes([0x00, 0xFE, 0xDC]), name="label_c0fedc")
                    )
                ],
            ),
            Instruction(
                position=Bytes([0x00, 0x00, 0x13]), opcode=Bytes([0xE2]), operands=[Operand(Bytes([0x30]), "#_")]
            ),
            Instruction(
                position=Bytes([0x00, 0x00, 0x15]),
                opcode=Bytes([0xA9]),
                operands=[
                    Operand(Bytes([0x00]), "#_", variable=Label(value=Bytes([0x00, 0xFE, 0xDC]), name="label_c0fedc"))
                ],
            ),
            Instruction(
                position=Bytes([0x00, 0x00, 0x17]), opcode=Bytes([0xA2]), operands=[Operand(Bytes([0xCC]), "#_")]
            ),
            Instruction(
                position=Bytes([0x00, 0x00, 0x19]),
                opcode=Bytes([0x44]),
                operands=[Operand(Bytes([0x34]), "#_"), Operand(Bytes([0x12]), "#_", variable=ALFA)],
            ),
            Instruction(
                position=Bytes([0x00, 0x00, 0x1C]),
                opcode=Bytes([0x4C]),
                operands=[
                    Operand(
                        Bytes([0x00, 0x05]),
                        "_",
                        OperandType.JUMPING,
                        variable=Label(value=Bytes([0x00, 0x00, 0x05]), name="archie"),
                    )
                ],
            ),
            Instruction(
                position=Bytes([0x00, 0x00, 0x1F]),
                opcode=Bytes([0x80]),
                operands=[
                    Operand(
                        Bytes([0xE0]),
                        "_",
                        OperandType.BRANCHING,
                        variable=Label(value=Bytes([0x00, 0x00, 0x01]), name="start"),
                    )
                ],
            ),
        ]

        self.script.blobs = [
            Blob(position=Bytes([0x00, 0x00, 0x21]), data=TEST_WORD),
            Blob(position=Bytes([0x00, 0x00, 0x23]), data=Bytes([0x56, 0x78]), delimiter=Bytes([0xFF])),
            Blob(position=Bytes([0x00, 0x00, 0x26]), data=Bytes([0xAB, 0xCD]), delimiter=Bytes([0x00])),
            String(
                position=Bytes([0x00, 0x00, 0x29]),
                data=Bytes([0x00, 0x80, 0xD8, 0xFF], endian=Endian.BIG),
                delimiter=Bytes([0x88]),
            ),
            String(
                position=Bytes([0x00, 0x00, 0x34]),
                data=Bytes([0x81, 0xA8, 0x9B, 0x01, 0xDC], endian=Endian.BIG),
                delimiter=Bytes([0x00]),
                string_type=StringTypes.DESCRIPTION,
            ),
        ]

        self.script.blob_groups = [
            BlobGroup(
                blobs=[
                    Blob(position=Bytes([0x00, 0x00, 0x2E]), data=Bytes([0xAA])),
                    String(position=Bytes([0x00, 0x00, 0x2F]), data=Bytes([0x9A])),
                    Blob(position=Bytes([0x00, 0x00, 0x30]), data=Bytes([0xBB]), delimiter=Bytes([0xFF])),
                    String(position=Bytes([0x00, 0x00, 0x32]), data=Bytes([0x9B]), delimiter=Bytes([0x00])),
                ],
                position=Bytes([0x00, 0x00, 0x2E]),
            )
        ]

        # Relative pointers
        self.script.pointers.append(
            Pointer(
                position=Bytes([0x00, 0x00, 0x3A]),
                destination=TEST_POSITION,
                anchor=Bytes([0x12, 0x00, 0x01]),
            )
        )
        self.script.pointers.append(
            Pointer(
                position=Bytes([0x00, 0x00, 0x3C]),
                destination=Bytes([0x12, 0x34, 0x57]),
                anchor=Bytes([0x12, 0x00, 0x01]),
            )
        )
        self.script.pointers.append(
            Pointer(
                position=Bytes([0x00, 0x00, 0x3E]),
                destination=Bytes([0x12, 0x34, 0x57]),
                anchor=Bytes([0x12, 0x00, 0x02]),
            )
        )


class TestScript:

    def test_from_script(self):
        script = Script.from_text_files(DUMMY_INPUT_SCRIPT_1, DUMMY_INPUT_SCRIPT_2)

        labels = script.variables.labels

        assert len(labels) == 5
        assert labels[0] == Label(value=Bytes([0x00, 0x00, 0x01]), name="start")
        assert labels[1] == Label(value=Bytes([0x00, 0x00, 0x05]), name="archie")
        assert labels[2] == Label(value=Bytes([0x12, 0x00, 0x01]), name="anchor_1")
        assert labels[3] == Label(value=TEST_POSITION, name="rptr_1")
        assert labels[4] == Label(value=Bytes([0x12, 0x34, 0x57]), name="rptr_2")

        assert len(script.pointers) == 5
        assert script.pointers[0] == Pointer(position=Bytes([0x00, 0x00, 0x01]), destination=Bytes([0x00, 0x12, 0x34]))
        assert script.pointers[1] == Pointer(position=Bytes([0x00, 0x00, 0x03]), destination=Bytes([0x00, 0x00, 0x05]))
        assert script.pointers[2] == Pointer(
            position=Bytes([0x00, 0x00, 0x3A]), anchor=Bytes([0x12, 0x00, 0x01]), destination=TEST_POSITION
        )
        assert script.pointers[3] == Pointer(
            position=Bytes([0x00, 0x00, 0x3C]), anchor=Bytes([0x12, 0x00, 0x01]), destination=Bytes([0x12, 0x34, 0x57])
        )
        assert script.pointers[4] == Pointer(
            position=Bytes([0x00, 0x00, 0x3E]), anchor=Bytes([0x12, 0x00, 0x02]), destination=Bytes([0x12, 0x34, 0x57])
        )

        assert len(script.instructions) == 12
        assert script.instructions[0] == Instruction(
            position=Bytes([0x00, 0x00, 0x05]), opcode=Bytes([0xAA]), operands=None
        )
        assert script.instructions[1] == Instruction(
            position=Bytes([0x00, 0x00, 0x06]),
            opcode=Bytes([0xA1]),
            operands=[Operand(TEST_BYTE, "(_,X)", variable=ALFA)],
        )
        assert script.instructions[2] == Instruction(
            position=Bytes([0x00, 0x00, 0x08]), opcode=Bytes([0xA2]), operands=[Operand(Bytes([0xFE, 0xDC]), "#_")]
        )

        assert script.instructions[3] == Instruction(
            position=Bytes([0x00, 0x00, 0x0B]), opcode=Bytes([0xC2]), operands=[Operand(Bytes([0x30]), "#_")]
        )
        assert script.instructions[4] == Instruction(
            position=Bytes([0x00, 0x00, 0x0D]),
            opcode=Bytes([0xA9]),
            operands=[Operand(Bytes([0x12, 0x34]), "#_", variable=BRAVO)],
        )
        assert script.instructions[5] == Instruction(
            position=Bytes([0x00, 0x00, 0x10]), opcode=Bytes([0xA2]), operands=[Operand(Bytes([0xFE, 0xDC]), "#_")]
        )

        assert script.instructions[6] == Instruction(
            position=Bytes([0x00, 0x00, 0x13]), opcode=Bytes([0xE2]), operands=[Operand(Bytes([0x30]), "#_")]
        )
        assert script.instructions[7] == Instruction(
            position=Bytes([0x00, 0x00, 0x15]), opcode=Bytes([0xA9]), operands=[Operand(Bytes([0xBB]), "#_")]
        )
        assert script.instructions[8] == Instruction(
            position=Bytes([0x00, 0x00, 0x17]), opcode=Bytes([0xA2]), operands=[Operand(Bytes([0xCC]), "#_")]
        )

        assert script.instructions[9] == Instruction(
            position=Bytes([0x00, 0x00, 0x19]),
            opcode=Bytes([0x44]),
            operands=[Operand(Bytes([0x34]), "#_"), Operand(Bytes([0x12]), "#_", variable=ALFA)],
        )
        assert script.instructions[10] == Instruction(
            position=Bytes([0x00, 0x00, 0x1C]),
            opcode=Bytes([0x4C]),
            operands=[
                Operand(
                    Bytes([0x00, 0x05]), "_", OperandType.JUMPING, Label(value=Bytes([0x00, 0x00, 0x05]), name="archie")
                )
            ],
        )
        assert script.instructions[11] == Instruction(
            position=Bytes([0x00, 0x00, 0x1F]),
            opcode=Bytes([0x80]),
            operands=[
                Operand(Bytes([0xE0]), "_", OperandType.BRANCHING, Label(value=Bytes([0x00, 0x00, 0x01]), name="start"))
            ],
        )

        assert len(script.blobs) == 5
        assert script.blobs[0] == Blob(position=Bytes([0x00, 0x00, 0x21]), data=TEST_WORD)
        assert script.blobs[1] == Blob(
            position=Bytes([0x00, 0x00, 0x23]), data=Bytes([0x56, 0x78]), delimiter=Bytes([0xFF])
        )
        assert script.blobs[2] == Blob(
            position=Bytes([0x00, 0x00, 0x26]), data=Bytes([0xAB, 0xCD]), delimiter=Bytes([0x00])
        )
        assert script.blobs[3] == String(
            position=Bytes([0x00, 0x00, 0x29]), data=Bytes([0x00, 0x80, 0xD8, 0xFE]), delimiter=Bytes([0x88])
        )
        assert script.blobs[4] == String(
            position=Bytes([0x00, 0x00, 0x34]),
            data=Bytes([0x81, 0xA8, 0x9B, 0x01, 0xDC]),
            delimiter=Bytes([0x00]),
            string_type=StringTypes.DESCRIPTION,
        )

        assert len(script.blob_groups) == 1
        assert len(script.blob_groups[0].blobs) == 4
        assert script.blob_groups[0].blobs[0] == Blob(position=Bytes([0x00, 0x00, 0x2E]), data=Bytes([0xAA]))
        assert script.blob_groups[0].blobs[1] == String(position=Bytes([0x00, 0x00, 0x2F]), data=Bytes([0x9A]))
        assert script.blob_groups[0].blobs[2] == Blob(
            position=Bytes([0x00, 0x00, 0x30]), data=Bytes([0xBB]), delimiter=Bytes([0xFF])
        )

    def test_from_script_file_raises_error_when_line_is_unrecognized(self):
        with pytest.raises(UnrecognizedLine) as e:
            Script.from_text_files(DUMMY_ERROR_SCRIPT)
        assert str(e.value) == "Line '  txt3 \"Lorem ipsum\"' is not recognized."

    def test_from_script_files_raises_error_when_lines_conflict(self):
        with pytest.raises(LineConflict) as e:
            Script.from_text_files(CONFLICTING_LINES_SCRIPT)
        assert (
            str(e.value)
            == "Lines '  LDA #$1234 ; C01234' and '  LDX #$5678 ; C01235' are conflicting with one another."
        )

    def test_from_script_files_raises_error_when_lines_conflict_in_multiple_files(self):
        with pytest.raises(LineConflict) as e:
            Script.from_text_files(CONFLICTING_FILE_1, CONFLICTING_FILE_2)
        assert str(e.value) == "Lines '  TAX ; C01237' and '  STA $1337 ; C01237' are conflicting with one another."

    def test_to_rom(self):
        with open(DUMMY_OUTPUT_ROM, "wb") as f:
            f.write(b"\x00")

        ScriptImpl().script.to_rom(output_path=DUMMY_OUTPUT_ROM)
        with open(DUMMY_OUTPUT_ROM, "rb") as f:
            output = f.read()

        assert output == (
            b"\x00"  # Script starts at byte 0x000001, so this is a byte of buffer
            b"\x34\x12\x05\x00"  # Pointers
            b"\xaa\xa1\x12\xa2\xdc\xfe"  # Instructions 0-2
            b"\xc2\x30\xa9\x34\x12\xa2\xdc\xfe"  # Instructions 3-5
            b"\xe2\x30\xa9\xc0\xa2\xcc"  # Instructions 6-8
            b"\x44\x34\x12\x4c\x05\x00\x80\xe0"  # Instructions 9-11
            b"\x34\x12\x78\x56\xff\xcd\xab\x00"  # Blobs 0-2
            b"\x00\x80\xd8\xff\x88"  # Menu String 0
            b"\xaa\x9a\xbb\xff\x9b\x00"  # Blob Group 0
            b"\x81\xa8\x9b\x01\xdc\x00"  # Description 0
            b"\x55\x34\x56\x34\x55\x34"  # Relative pointers 0-2
        )

    def test_from_rom(self):
        sections = [
            ScriptSection(start=0x000000, end=0x000008, mode=ScriptMode.POINTERS),
            ScriptSection(start=0x000008, end=0x000012, mode=ScriptMode.INSTRUCTIONS, flags=Flags()),
            ScriptSection(start=0x000012, end=0x000014, mode=ScriptMode.BLOBS, length=2),
            ScriptSection(start=0x000014, end=0x000017, mode=ScriptMode.BLOBS, delimiter=Bytes([0xFF])),
            ScriptSection(start=0x000017, end=0x00001A, mode=ScriptMode.BLOBS, delimiter=Bytes([0x00])),
            ScriptSection(
                start=0x00001A,
                end=0x00001F,
                mode=ScriptMode.MENU_STRINGS,
                delimiter=b"\x88",
                charset=Charset(charset=MENU_CHARSET),
            ),
            ScriptSection(
                start=0x00001F,
                end=0x000025,
                mode=ScriptMode.BLOB_GROUPS,
                sub_sections=[
                    SubSection(mode=ScriptMode.BLOBS, length=1),
                    SubSection(mode=ScriptMode.MENU_STRINGS, length=1),
                    SubSection(mode=ScriptMode.BLOBS, delimiter=Bytes([0xFF])),
                    SubSection(mode=ScriptMode.MENU_STRINGS, delimiter=Bytes([0x00])),
                ],
            ),
        ]
        script = Script.from_rom(filename=DUMMY_INPUT_ROM, sections=sections)

        assert len(script.pointers) == 4
        assert script.pointers[0] == Pointer(position=Bytes([0x00, 0x00, 0x00]), destination=Bytes([0x00, 0x23, 0x01]))
        assert script.pointers[1] == Pointer(position=Bytes([0x00, 0x00, 0x02]), destination=Bytes([0x00, 0x67, 0x45]))
        assert script.pointers[2] == Pointer(position=Bytes([0x00, 0x00, 0x04]), destination=Bytes([0x00, 0xAB, 0x89]))
        assert script.pointers[3] == Pointer(position=Bytes([0x00, 0x00, 0x06]), destination=Bytes([0x00, 0xEF, 0xCD]))

        assert len(script.instructions) == 5
        assert script.instructions[0] == Instruction(position=Bytes([0x00, 0x00, 0x08]), opcode=Bytes([0x00]))
        assert script.instructions[1] == Instruction(position=Bytes([0x00, 0x00, 0x09]), opcode=Bytes([0xAA]))
        assert script.instructions[2] == Instruction(
            position=Bytes([0x00, 0x00, 0x0A]), opcode=Bytes([0xA9]), operands=[Operand(Bytes([0x34, 0x56]), "#_")]
        )
        assert script.instructions[3] == Instruction(
            position=Bytes([0x00, 0x00, 0x0D]), opcode=Bytes([0xA2]), operands=[Operand(Bytes([0xFE, 0xDC]), "#_")]
        )
        assert script.instructions[4] == Instruction(
            position=Bytes([0x00, 0x00, 0x10]),
            opcode=Bytes([0x80]),
            operands=[Operand(Bytes([0xFE]), "_", OperandType.BRANCHING, Label(Bytes.from_position(0x10)))],
        )

        assert len(script.blobs) == 4
        assert script.blobs[0] == Blob(position=Bytes([0x00, 0x00, 0x12]), data=TEST_WORD)
        assert script.blobs[1] == Blob(
            position=Bytes([0x00, 0x00, 0x14]), data=Bytes([0x56, 0x78]), delimiter=Bytes([0xFF])
        )
        assert script.blobs[2] == Blob(
            position=Bytes([0x00, 0x00, 0x17]), data=Bytes([0xCD, 0xAB]), delimiter=Bytes([0x00])
        )
        assert script.blobs[3] == Blob(
            position=Bytes([0x00, 0x00, 0x1A]), data=Bytes([0x00, 0x80, 0xD8, 0xFF]), delimiter=Bytes([0x88])
        )

        labels = script.variables.labels

        assert len(labels) == 5
        assert labels[0] == Label(value=Bytes([0x00, 0x00, 0x10]))
        assert labels[1] == Label(value=Bytes([0x00, 0x23, 0x01]))
        assert labels[2] == Label(value=Bytes([0x00, 0x67, 0x45]))
        assert labels[3] == Label(value=Bytes([0x00, 0xAB, 0x89]))
        assert labels[4] == Label(value=Bytes([0x00, 0xEF, 0xCD]))

    def test_to_script_file(self):
        ScriptImpl().script.to_text_file(filename=DUMMY_OUTPUT_SCRIPT, flags=Flags(m=8, x=8))
        with open(DUMMY_OUTPUT_SCRIPT) as f:
            script = f.read()
        assert script == (
            """m=8,x=8

db alfa = $12
dw bravo = $1234

@start = $C00001
  ptr label_c01234
  ptr archie
@archie
  TAX
  LDA (alfa,X)
  LDX #$FEDC
  REP #$30
  LDA #bravo
  LDX #!label_c0fedc
  SEP #$30
  LDA #.label_c0fedc
  LDX #$CC
  MVP #$34,#alfa
  JMP !archie
  BRA start
  $1234
  $5678,$FF
  $ABCD,$00
  "<0x00>A<KNIFE>_",$88
  $AA | "a" | $BB,$FF | "b",$00
  txt2 "Bob<LINE><FIRE>",$00

#anchor_1
  rptr label_d23456
  rptr label_d23457

#$D20002
  rptr label_d23457

@label_c01234 = $C01234

@label_c0fedc = $C0FEDC

@anchor_1 = $D20001

@label_d23456 = $D23456

@label_d23457 = $D23457"""
        )
