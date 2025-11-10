from pathlib import Path

import pytest

from src.lib.structures.asm.blob import Blob
from src.lib.structures.asm.blob_group import BlobGroup
from src.lib.structures.asm.string import String, StringTypes
from src.lib.structures.bytes import LEBytes, Position, BEBytes
from src.lib.structures.asm.flags import Flags
from src.lib.structures.asm.instruction import Instruction, BranchingInstruction
from src.lib.structures.asm.label import Label
from src.lib.structures.asm.pointer import Pointer
from src.lib.structures.asm.script import Script, ScriptMode, ScriptSection, SubSection, UnrecognizedLine
from src.lib.structures.charset.charset import MENU_CHARSET, Charset
from test import TEST_FOLDER

DUMMY_INPUT_SCRIPT = Path(TEST_FOLDER, "dummy_input_script.asm")
DUMMY_ERROR_SCRIPT = Path(TEST_FOLDER, "dummy_error_script.asm")
DUMMY_OUTPUT_SCRIPT = Path(TEST_FOLDER, "dummy_output_script.asm")
DUMMY_INPUT_ROM = Path(TEST_FOLDER, "dummy_input_rom.sfc")
DUMMY_OUTPUT_ROM = Path(TEST_FOLDER, "dummy_output_rom.sfc")


class ScriptImpl:
    def __init__(self):
        self.script = Script()

        self.script.flags = Flags()

        self.script.labels = [
            Label(position=Position([0x00, 0x00, 0x01]), name="start"),
            Label(position=Position([0x00, 0x00, 0x05]), name="archie"),
        ]

        self.script.pointers = [
            Pointer(position=Position([0x00, 0x00, 0x01]), destination=Position([0x00, 0x12, 0x34])),
            Pointer(position=Position([0x00, 0x00, 0x03]), destination=Position([0x00, 0x00, 0x05])),
        ]

        self.script.instructions = [
            Instruction(position=Position([0x00, 0x00, 0x05]), opcode=LEBytes([0xAA]), data=None),
            Instruction(position=Position([0x00, 0x00, 0x06]), opcode=LEBytes([0xA1]), data=LEBytes([0x12])),
            Instruction(position=Position([0x00, 0x00, 0x08]), opcode=LEBytes([0xA2]), data=LEBytes([0xFE, 0xDC])),
            Instruction(position=Position([0x00, 0x00, 0x0B]), opcode=LEBytes([0xC2]), data=LEBytes([0x30])),
            Instruction(position=Position([0x00, 0x00, 0x0D]), opcode=LEBytes([0xA9]), data=LEBytes([0x34, 0x56])),
            Instruction(position=Position([0x00, 0x00, 0x10]), opcode=LEBytes([0xA2]), data=LEBytes([0xFE, 0xDC])),
            Instruction(position=Position([0x00, 0x00, 0x13]), opcode=LEBytes([0xE2]), data=LEBytes([0x30])),
            Instruction(position=Position([0x00, 0x00, 0x15]), opcode=LEBytes([0xA9]), data=LEBytes([0xBB])),
            Instruction(position=Position([0x00, 0x00, 0x17]), opcode=LEBytes([0xA2]), data=LEBytes([0xCC])),
            Instruction(position=Position([0x00, 0x00, 0x19]), opcode=LEBytes([0x44]), data=LEBytes([0x34, 0x12])),
        ]

        self.script.branching_instructions = [
            BranchingInstruction(
                position=Position([0x00, 0x00, 0x1C]), opcode=LEBytes([0x4C]), data=LEBytes([0x00, 0x05])
            ),
            BranchingInstruction(position=Position([0x00, 0x00, 0x1F]), opcode=LEBytes([0x80]), data=LEBytes([0xE0])),
        ]

        self.script.blobs = [
            Blob(position=Position([0x00, 0x00, 0x21]), data=LEBytes([0x12, 0x34])),
            Blob(position=Position([0x00, 0x00, 0x23]), data=LEBytes([0x56, 0x78]), delimiter=LEBytes([0xFF])),
            Blob(position=Position([0x00, 0x00, 0x26]), data=LEBytes([0xAB, 0xCD]), delimiter=LEBytes([0x00])),
            String(
                position=Position([0x00, 0x00, 0x29]), data=BEBytes([0x00, 0x80, 0xD8, 0xFF]), delimiter=LEBytes([0x88])
            ),
            String(
                position=Position([0x00, 0x00, 0x34]),
                data=BEBytes([0x81, 0xA8, 0x9B, 0x01, 0xDC]),
                delimiter=LEBytes([0x00]),
                string_type=StringTypes.DESCRIPTION,
            ),
        ]

        self.script.blob_groups = [
            BlobGroup(
                blobs=[
                    Blob(position=Position([0x00, 0x00, 0x2E]), data=LEBytes([0xAA])),
                    String(position=Position([0x00, 0x00, 0x2F]), data=BEBytes([0x9A])),
                    Blob(position=Position([0x00, 0x00, 0x30]), data=LEBytes([0xBB]), delimiter=LEBytes([0xFF])),
                    String(position=Position([0x00, 0x00, 0x32]), data=BEBytes([0x9B]), delimiter=LEBytes([0x00])),
                ],
                position=Position([0x00, 0x00, 0x2E]),
            )
        ]


class TestScript:

    def test_from_script(self):
        script = Script.from_script_file(filename=DUMMY_INPUT_SCRIPT)

        assert len(script.labels) == 2
        assert script.labels[0] == Label(position=Position([0x00, 0x00, 0x01]), name="start")
        assert script.labels[1] == Label(position=Position([0x00, 0x00, 0x05]), name="archie")

        assert len(script.pointers) == 2
        assert script.pointers[0] == Pointer(
            position=Position([0x00, 0x00, 0x01]), destination=Position([0x00, 0x12, 0x34])
        )
        assert script.pointers[1] == Pointer(
            position=Position([0x00, 0x00, 0x03]), destination=Position([0x00, 0x00, 0x05])
        )

        assert len(script.instructions) == 10
        assert script.instructions[0] == Instruction(
            position=Position([0x00, 0x00, 0x05]), opcode=LEBytes([0xAA]), data=None
        )
        assert script.instructions[1] == Instruction(
            position=Position([0x00, 0x00, 0x06]), opcode=LEBytes([0xA1]), data=LEBytes([0x12])
        )
        assert script.instructions[2] == Instruction(
            position=Position([0x00, 0x00, 0x08]), opcode=LEBytes([0xA2]), data=LEBytes([0xFE, 0xDC])
        )

        assert script.instructions[3] == Instruction(
            position=Position([0x00, 0x00, 0x0B]), opcode=LEBytes([0xC2]), data=LEBytes([0x30])
        )
        assert script.instructions[4] == Instruction(
            position=Position([0x00, 0x00, 0x0D]), opcode=LEBytes([0xA9]), data=LEBytes([0x34, 0x56])
        )
        assert script.instructions[5] == Instruction(
            position=Position([0x00, 0x00, 0x10]), opcode=LEBytes([0xA2]), data=LEBytes([0xFE, 0xDC])
        )

        assert script.instructions[6] == Instruction(
            position=Position([0x00, 0x00, 0x13]), opcode=LEBytes([0xE2]), data=LEBytes([0x30])
        )
        assert script.instructions[7] == Instruction(
            position=Position([0x00, 0x00, 0x15]), opcode=LEBytes([0xA9]), data=LEBytes([0xBB])
        )
        assert script.instructions[8] == Instruction(
            position=Position([0x00, 0x00, 0x17]), opcode=LEBytes([0xA2]), data=LEBytes([0xCC])
        )

        assert script.instructions[9] == Instruction(
            position=Position([0x00, 0x00, 0x19]), opcode=LEBytes([0x44]), data=LEBytes([0x12, 0x34])
        )

        assert len(script.branching_instructions) == 2
        assert script.branching_instructions[0] == BranchingInstruction(
            position=Position([0x00, 0x00, 0x1C]), opcode=LEBytes([0x4C]), data=LEBytes([0x00, 0x05])
        )
        assert script.branching_instructions[1] == BranchingInstruction(
            position=Position([0x00, 0x00, 0x1F]), opcode=LEBytes([0x80]), data=LEBytes([0xE0])
        )

        assert len(script.blobs) == 5
        assert script.blobs[0] == Blob(position=Position([0x00, 0x00, 0x21]), data=LEBytes([0x12, 0x34]))
        assert script.blobs[1] == Blob(
            position=Position([0x00, 0x00, 0x23]), data=LEBytes([0x56, 0x78]), delimiter=LEBytes([0xFF])
        )
        assert script.blobs[2] == Blob(
            position=Position([0x00, 0x00, 0x26]), data=LEBytes([0xAB, 0xCD]), delimiter=LEBytes([0x00])
        )
        assert script.blobs[3] == String(
            position=Position([0x00, 0x00, 0x29]), data=BEBytes([0x00, 0x80, 0xD8, 0xFF]), delimiter=LEBytes([0x88])
        )
        assert script.blobs[4] == String(
            position=Position([0x00, 0x00, 0x34]),
            data=BEBytes([0x81, 0xA8, 0x9B, 0x01, 0xDC]),
            delimiter=LEBytes([0x00]),
            string_type=StringTypes.DESCRIPTION,
        )

        assert len(script.blob_groups) == 1
        assert len(script.blob_groups[0].blobs) == 4
        assert script.blob_groups[0].blobs[0] == Blob(position=Position([0x00, 0x00, 0x2E]), data=LEBytes([0xAA]))
        assert script.blob_groups[0].blobs[1] == String(position=Position([0x00, 0x00, 0x2F]), data=BEBytes([0x9A]))
        assert script.blob_groups[0].blobs[2] == Blob(
            position=Position([0x00, 0x00, 0x30]), data=LEBytes([0xBB]), delimiter=LEBytes([0xFF])
        )

    def test_from_script_file_raises_error_when_line_is_unrecognized(self):
        with pytest.raises(UnrecognizedLine) as e:
            Script.from_script_file(DUMMY_ERROR_SCRIPT)
        assert str(e.value) == "Line '  txt3 \"Lorem ipsum\"' is not recognized."

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
            b"\xc2\x30\xa9\x56\x34\xa2\xdc\xfe"  # Instructions 3-5
            b"\xe2\x30\xa9\xbb\xa2\xcc"  # Instructions 6-8
            b"\x44\x12\x34\x4c\x05\x00\x80\xe0"  # Instructions 9-11
            b"\x34\x12\x78\x56\xff\xcd\xab\x00"  # Blobs 0-2
            b"\x00\x80\xd8\xff\x88"  # Menu String 0
            b"\xaa\x9a\xbb\xff\x9b\x00"  # Blob Group 0
            b"\x81\xa8\x9b\x01\xdc\x00"  # Description 0
        )

    def test_from_rom(self):
        sections = [
            ScriptSection(start=0x000000, end=0x000008, mode=ScriptMode.POINTERS),
            ScriptSection(start=0x000008, end=0x000012, mode=ScriptMode.INSTRUCTIONS, flags=Flags()),
            ScriptSection(start=0x000012, end=0x000014, mode=ScriptMode.BLOBS, length=2),
            ScriptSection(start=0x000014, end=0x000017, mode=ScriptMode.BLOBS, delimiter=LEBytes([0xFF])),
            ScriptSection(start=0x000017, end=0x00001A, mode=ScriptMode.BLOBS, delimiter=LEBytes([0x00])),
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
                    SubSection(mode=ScriptMode.BLOBS, delimiter=LEBytes([0xFF])),
                    SubSection(mode=ScriptMode.MENU_STRINGS, delimiter=LEBytes([0x00])),
                ],
            ),
        ]
        script = Script.from_rom(filename=DUMMY_INPUT_ROM, sections=sections)

        assert len(script.pointers) == 4
        assert script.pointers[0] == Pointer(position=Position([0x00, 0x00, 0x00]), destination=Position([0x23, 0x01]))
        assert script.pointers[1] == Pointer(position=Position([0x00, 0x00, 0x02]), destination=Position([0x67, 0x45]))
        assert script.pointers[2] == Pointer(position=Position([0x00, 0x00, 0x04]), destination=Position([0xAB, 0x89]))
        assert script.pointers[3] == Pointer(position=Position([0x00, 0x00, 0x06]), destination=Position([0xEF, 0xCD]))

        assert len(script.instructions) == 4
        assert script.instructions[0] == Instruction(position=Position([0x00, 0x00, 0x08]), opcode=LEBytes([0x00]))
        assert script.instructions[1] == Instruction(position=Position([0x00, 0x00, 0x09]), opcode=LEBytes([0xAA]))
        assert script.instructions[2] == Instruction(
            position=Position([0x00, 0x00, 0x0A]), opcode=LEBytes([0xA9]), data=LEBytes([0x34, 0x56])
        )
        assert script.instructions[3] == Instruction(
            position=Position([0x00, 0x00, 0x0D]), opcode=LEBytes([0xA2]), data=LEBytes([0xFE, 0xDC])
        )

        assert len(script.branching_instructions) == 1
        assert script.branching_instructions[0] == BranchingInstruction(
            position=Position([0x00, 0x00, 0x10]), opcode=LEBytes([0x80]), data=LEBytes([0xFE])
        )

        assert len(script.blobs) == 4
        assert script.blobs[0] == Blob(position=Position([0x00, 0x00, 0x12]), data=LEBytes([0x12, 0x34]))
        assert script.blobs[1] == Blob(
            position=Position([0x00, 0x00, 0x14]), data=LEBytes([0x56, 0x78]), delimiter=LEBytes([0xFF])
        )
        assert script.blobs[2] == Blob(
            position=Position([0x00, 0x00, 0x17]), data=LEBytes([0xCD, 0xAB]), delimiter=LEBytes([0x00])
        )
        assert script.blobs[3] == Blob(
            position=Position([0x00, 0x00, 0x1A]), data=LEBytes([0x00, 0x80, 0xD8, 0xFF]), delimiter=LEBytes([0x88])
        )

        assert len(script.labels) == 5
        assert script.labels[0] == Label(position=Position([0x00, 0x23, 0x01]))
        assert script.labels[1] == Label(position=Position([0x00, 0x67, 0x45]))
        assert script.labels[2] == Label(position=Position([0x00, 0xAB, 0x89]))
        assert script.labels[3] == Label(position=Position([0x00, 0xEF, 0xCD]))
        assert script.labels[4] == Label(position=Position([0x00, 0x00, 0x10]))

    def test_to_script_file(self):
        ScriptImpl().script.to_script_file(filename=DUMMY_OUTPUT_SCRIPT, flags=Flags(m=True, x=True))
        with open(DUMMY_OUTPUT_SCRIPT) as f:
            script = f.read()
        assert script == (
            """m=8,x=8

@start=C00001
  ptr label_c01234
  ptr archie
@archie
  TAX
  LDA ($12,X)
  LDX #$FEDC
  REP #$30
  LDA #$3456
  LDX #$FEDC
  SEP #$30
  LDA #$BB
  LDX #$CC
  MVP #$34,#$12
  JMP archie
  BRA start
  $1234
  $5678,$FF
  $ABCD,$00
  "<0x00>A<KNIFE>_",$88
  $AA | "a" | $BB,$FF | "b",$00
  txt2 "Bob<LINE><FIRE>",$00

@label_c01234=C01234"""
        )
