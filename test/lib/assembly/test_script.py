from pathlib import Path

import pytest

from src.lib.assembly.artifact.flags import Flags
from src.lib.assembly.artifact.variable import Label, SimpleVar
from src.lib.assembly.bytes import Bytes, Endian
from src.lib.assembly.data_structure.array import Array
from src.lib.assembly.data_structure.blob import Blob
from src.lib.assembly.data_structure.instruction.instruction import Instruction
from src.lib.assembly.data_structure.instruction.operand import Operand, OperandType
from src.lib.assembly.data_structure.pointer import Pointer
from src.lib.assembly.data_structure.string.charset import MENU_CHARSET, Charset, DESCRIPTION_CHARSET
from src.lib.assembly.data_structure.string.string import String, StringTypes
from src.lib.assembly.script.helpers import ScriptMode, ScriptSection, SubSection, Line, LineType
from src.lib.assembly.script.script import (
    Script,
)
from src.lib.misc.exception import LineConflict, UnrecognizedLine
from test import RESOURCES_FOLDER
from test.lib.assembly.conftest import TEST_BYTE, TEST_WORD, TEST_POSITION, ALFA, BRAVO, pos, DELTA

CONFLICTING_FILE_1 = Path(RESOURCES_FOLDER, "conflicting_file_1.asm")
CONFLICTING_FILE_2 = Path(RESOURCES_FOLDER, "conflicting_file_2.asm")
CONFLICTING_FLAGS_SCRIPT = Path(RESOURCES_FOLDER, "conflicting_flags.asm")
CONFLICTING_LABELS_SCRIPT = Path(RESOURCES_FOLDER, "conflicting_labels_script.asm")
CONFLICTING_LINES_SCRIPT = Path(RESOURCES_FOLDER, "conflicting_lines_script.asm")
DUMMY_INPUT_SCRIPT_1 = Path(RESOURCES_FOLDER, "dummy_input_script_1.asm")
DUMMY_INPUT_SCRIPT_2 = Path(RESOURCES_FOLDER, "dummy_input_script_2.asm")
DUMMY_ERROR_SCRIPT = Path(RESOURCES_FOLDER, "dummy_error_script.asm")
DUMMY_OUTPUT_SCRIPT = Path(RESOURCES_FOLDER, "dummy_output_script.asm")
DUMMY_INPUT_ROM = Path(RESOURCES_FOLDER, "dummy_input_rom.sfc")
DUMMY_OUTPUT_ROM = Path(RESOURCES_FOLDER, "dummy_output_rom.sfc")

LABELS = [
    Label(pos(0x000001), "start"),
    Label(pos(0x000005), "archie"),
    Label(pos(0x001234)),
    Label(pos(0x00FEDC)),
    Label(pos(0x120001), "anchor_1"),
    Label(pos(0x123456), "rptr_1"),
    Label(pos(0x123457), "rptr_2"),
]


class ScriptImpl:
    def __init__(self):
        self.script = Script()

        self.script.lines = [
            Line(
                raw_line="m = 8, x = 16",
                clean_line="m = 8, x = 16",
                position=0x000000,
                component_info=LineType.FLAGS,
                regex_groups={"m_flag": "8", "x_flag": "16"},
                component=Flags(m=8),
                filename=DUMMY_INPUT_SCRIPT_1,
            ),
            Line(
                raw_line="db alfa = $12",
                clean_line="db alfa = $12",
                position=0x000000,
                component_info=LineType.VARIABLE_DECLARATION,
                regex_groups=None,
                component=ALFA,
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="dw bravo = $1234",
                clean_line="dw bravo = $1234",
                position=0x000000,
                component_info=LineType.VARIABLE_DECLARATION,
                regex_groups=None,
                component=BRAVO,
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="db delta = $00",
                clean_line="db delta = $00",
                position=0x000000,
                component_info=LineType.VARIABLE_DECLARATION,
                regex_groups=None,
                component=DELTA,
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="@start = $C00001",
                clean_line="@start = $C00001",
                position=0x000001,
                component_info=LineType.LABEL,
                regex_groups={"name": "start", "snes_address": "$C00001"},
                component=LABELS[0],
                filename=DUMMY_INPUT_SCRIPT_1,
            ),
            Line(
                raw_line="  ptr $1234",
                clean_line="ptr $1234",
                position=0x000001,
                component_info=LineType.POINTER,
                regex_groups={"operand": "$1234"},
                component=Pointer(position=pos(0x000001), operand=Operand(Bytes([0x12, 0x34]))),
                filename=DUMMY_INPUT_SCRIPT_1,
            ),
            Line(
                raw_line="  ptr $0005",
                clean_line="ptr $0005",
                position=0x000003,
                component_info=LineType.POINTER,
                regex_groups={"operand": "$0005"},
                component=Pointer(position=pos(0x000003), operand=Operand(Bytes([0x00, 0x05]))),
                filename=DUMMY_INPUT_SCRIPT_1,
            ),
            Line(
                raw_line="@archie = $C00005",
                clean_line="@archie = $C00005",
                position=0x000005,
                component_info=LineType.LABEL,
                regex_groups={"name": "archie", "snes_address": "$C00005"},
                component=LABELS[1],
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="  TAX ; some comment",
                clean_line="TAX",
                position=0x000005,
                component_info=LineType.INSTRUCTION,
                regex_groups={"command": "TAX", "operand": None},
                component=Instruction(position=pos(0x000005), opcode=Bytes([0xAA]), operands=None),
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="  LDA (alfa,X)",
                clean_line="LDA(alfa, X)",
                position=0x000006,
                component_info=LineType.INSTRUCTION,
                regex_groups={"command": "LDA", "operand": "(alfa, X)"},
                component=Instruction(
                    position=pos(0x000006),
                    opcode=Bytes([0xA1]),
                    operands=[Operand(TEST_BYTE, "(_,X)", variable=ALFA)],
                ),
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="  LDX #$FEDC",
                clean_line="LDX #$FEDC",
                position=0x000008,
                component_info=LineType.INSTRUCTION,
                regex_groups={"command": "LDX", "operand": "#$FEDC"},
                component=Instruction(
                    position=pos(0x000008), opcode=Bytes([0xA2]), operands=[Operand(Bytes([0xFE, 0xDC]), "#_")]
                ),
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="  REP #$30",
                clean_line="REP #$30",
                position=0x00000B,
                component_info=LineType.INSTRUCTION,
                regex_groups={"command": "REP", "operand": "#$30"},
                component=Instruction(
                    position=pos(0x00000B), opcode=Bytes([0xC2]), operands=[Operand(Bytes([0x30]), "#_")]
                ),
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="  LDA #bravo",
                clean_line="LDA #bravo",
                position=0x00000D,
                component_info=LineType.INSTRUCTION,
                regex_groups={"command": "LDA", "operand": "#bravo"},
                component=Instruction(
                    position=pos(0x00000D),
                    opcode=Bytes([0xA9]),
                    operands=[Operand(Bytes([0x12, 0x34]), "#_", variable=BRAVO)],
                ),
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="  LDX #$FEDC",
                clean_line="LDX #$FEDC",
                position=0x000010,
                component_info=LineType.INSTRUCTION,
                regex_groups={"command": "LDX", "operand": "#$FEDC"},
                component=Instruction(
                    position=pos(0x000010), opcode=Bytes([0xA2]), operands=[Operand(Bytes([0xFE, 0xDC]), "#_")]
                ),
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="  SEP #$30",
                clean_line="SEP #$30",
                position=0x000013,
                component_info=LineType.INSTRUCTION,
                regex_groups={"command": "SEP", "operand": "#$30"},
                component=Instruction(
                    position=pos(0x000013), opcode=Bytes([0xE2]), operands=[Operand(Bytes([0x30]), "#_")]
                ),
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="  LDA #.label_c0fedc",
                clean_line="LDA #.label_c0fedc",
                position=0x000015,
                component_info=LineType.INSTRUCTION,
                regex_groups={"command": "LDA", "operand": "#.label_c0fedc"},
                component=Instruction(
                    position=pos(0x000015),
                    opcode=Bytes([0xA9]),
                    operands=[Operand(Bytes([0xC0]), "#_", variable=LABELS[3])],
                ),
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="  LDX #$CC",
                clean_line="LDX #$CC",
                position=0x000017,
                component_info=LineType.INSTRUCTION,
                regex_groups={"command": "LDX", "operand": "#$CC"},
                component=Instruction(
                    position=pos(0x000017), opcode=Bytes([0xA2]), operands=[Operand(Bytes([0xCC]), "#_")]
                ),
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="  MVP #$34,#alfa",
                clean_line="MVP #$34,#alfa",
                position=0x000019,
                component_info=LineType.INSTRUCTION,
                regex_groups={"command": "MVP", "operand": "#$34,#alfa"},
                component=Instruction(
                    position=pos(0x000019),
                    opcode=Bytes([0x44]),
                    operands=[Operand(Bytes([0x34]), "#_"), Operand(Bytes([0x12]), "#_", variable=ALFA)],
                ),
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="  JMP !archie",
                clean_line="JMP !archie",
                position=0x00001C,
                component_info=LineType.INSTRUCTION,
                regex_groups={"command": "JMP", "operand": "!archie"},
                component=Instruction(
                    position=pos(0x00001C),
                    opcode=Bytes([0x4C]),
                    operands=[Operand(Bytes([0x00, 0x05]), "_", OperandType.JUMPING, LABELS[1])],
                ),
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="  BRA start ; some other comment",
                clean_line="BRA start",
                position=0x00001F,
                component_info=LineType.INSTRUCTION,
                regex_groups={"command": "BRA", "operand": "start"},
                component=Instruction(
                    position=pos(0x00001F),
                    opcode=Bytes([0x80]),
                    operands=[Operand(Bytes([0xE0]), "_", OperandType.BRANCHING, LABELS[0])],
                ),
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="  bravo",
                clean_line="bravo",
                position=0x000021,
                component_info=LineType.BLOB,
                regex_groups={"operand": "bravo", "delimiter": None},
                component=Blob(position=pos(0x000021), operand=Operand(TEST_WORD, variable=BRAVO)),
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="  $5678,$FF",
                clean_line="$5678,$FF",
                position=0x000023,
                component_info=LineType.BLOB,
                regex_groups={"operand": "$5678", "delimiter": "$FF"},
                component=Blob(
                    position=pos(0x000023), operand=Operand(Bytes([0x56, 0x78])), delimiter=Operand(Bytes([0xFF]))
                ),
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="  $ABCD,delta",
                clean_line="$ABCD,delta",
                position=0x000026,
                component_info=LineType.BLOB,
                regex_groups={"operand": "$ABCD", "delimiter": "delta"},
                component=Blob(
                    position=pos(0x000026),
                    operand=Operand(Bytes([0xAB, 0xCD])),
                    delimiter=Operand(Bytes([0x00]), variable=DELTA),
                ),
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line='  "<0x00>A<KNIFE>_",$88',
                clean_line='"<0x00>A<KNIFE>_",$88',
                position=0x000029,
                component_info=LineType.STRING,
                regex_groups={"string_type": None, "string": "<0x00>A<KNIFE>_", "delimiter": "$88"},
                component=String(
                    position=pos(0x000029),
                    operand=Operand(Bytes([0x00, 0x80, 0xD8, 0xFF], endian=Endian.BIG)),
                    delimiter=Operand(Bytes([0x88])),
                ),
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line='  $AA | "a" | $BB,$FF | "b",$00',
                clean_line='$AA | "a" | $BB,$FF | "b",$00',
                position=0x00002E,
                component_info=LineType.ARRAY,
                regex_groups={},
                component=Array(
                    position=pos(0x00002E),
                    parts=[
                        Blob(position=pos(0x00002E), operand=Operand(Bytes([0xAA]))),
                        String(position=pos(0x00002F), operand=Operand(Bytes([0x9A], endian=Endian.BIG))),
                        Blob(position=pos(0x000030), operand=Operand(Bytes([0xBB])), delimiter=Operand(Bytes([0xFF]))),
                        String(
                            position=pos(0x000032),
                            operand=Operand(Bytes([0x9B], endian=Endian.BIG)),
                            delimiter=Operand(Bytes([0x00])),
                        ),
                    ],
                ),
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line='  desc "Bob<LINE><FIRE>",$00',
                clean_line='desc "Bob<LINE><FIRE>",$00',
                position=0x000034,
                component_info=LineType.STRING,
                regex_groups={"string_type": "desc", "string": "Bob<LINE><FIRE>", "delimiter": "$00"},
                component=String(
                    position=pos(0x000034),
                    operand=Operand(Bytes([0x81, 0xA8, 0x9B, 0x01, 0xDC], endian=Endian.BIG)),
                    charset=DESCRIPTION_CHARSET,
                    string_type=StringTypes.DESCRIPTION,
                    delimiter=Operand(Bytes([0x00])),
                ),
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="#anchor_1",
                clean_line="#anchor_1",
                position=0x00003A,
                component_info=LineType.ANCHOR,
                regex_groups={"value": "anchor_1"},
                component=None,
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="  rptr !rptr_1",
                clean_line="rptr !rptr_1",
                position=0x00003A,
                component_info=LineType.POINTER,
                regex_groups={"operand": "!rptr_1"},
                component=Pointer(
                    position=pos(0x00003A),
                    anchor=Operand(Bytes([0x12, 0x00, 0x01]), variable=LABELS[4]),
                    operand=Operand(Bytes([0x34, 0x55]), variable=LABELS[5]),
                ),
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="  rptr !rptr_2",
                clean_line="rptr !rptr_2",
                position=0x00003C,
                component_info=LineType.POINTER,
                regex_groups={"operand": "!rptr_2"},
                component=Pointer(
                    position=Bytes.from_position(0x00003C),
                    anchor=Operand(Bytes([0x12, 0x00, 0x01]), variable=LABELS[4]),
                    operand=Operand(Bytes([0x34, 0x56]), variable=LABELS[6]),
                ),
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="#$D20002",
                clean_line="# $D20002",
                position=62,
                component_info=LineType.ANCHOR,
                regex_groups={"value": "$D20002"},
                component=None,
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="  rptr !rptr_2",
                clean_line="rptr !rptr_2",
                position=62,
                component_info=LineType.POINTER,
                regex_groups={"operand": "!rptr_2"},
                component=Pointer(
                    position=Bytes([0x00, 0x00, 0x3E]),
                    anchor=Operand(Bytes([0x12, 0x00, 0x02])),
                    operand=Operand(Bytes([0x34, 0x55]), variable=LABELS[6]),
                ),
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="@anchor_1 = $D20001",
                clean_line="@anchor_1 = $D20001",
                position=1179649,
                component_info=LineType.LABEL,
                regex_groups={"name": "anchor_1", "snes_address": "$D20001"},
                component=LABELS[4],
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="@rptr_1 = $D23456",
                clean_line="@rptr_1 = $D23456",
                position=1193046,
                component_info=LineType.LABEL,
                regex_groups={"name": "rptr_1", "snes_address": "$D23456"},
                component=LABELS[5],
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
            Line(
                raw_line="@rptr_2 = $D23457",
                clean_line="@rptr_2 = $D23457",
                position=1193047,
                component_info=LineType.LABEL,
                regex_groups={"name": "rptr_2", "snes_address": "$D23457"},
                component=LABELS[6],
                filename=DUMMY_INPUT_SCRIPT_2,
            ),
        ]


class TestScript:

    def test_from_script(self):
        script = Script.from_text_files(DUMMY_INPUT_SCRIPT_1, DUMMY_INPUT_SCRIPT_2)

        labels = script.labels()

        for line in script.lines:
            print(repr(line))

        assert len(labels) == 6
        assert labels[0] == Label(pos(0x000001), "start")
        assert labels[1] == Label(pos(0x000005), "archie")
        assert labels[2] == Label(pos(0x00FEDC), "label_c0fedc")
        assert labels[3] == Label(value=Bytes([0x12, 0x00, 0x01]), name="anchor_1")
        assert labels[4] == Label(value=TEST_POSITION, name="rptr_1")
        assert labels[5] == Label(value=Bytes([0x12, 0x34, 0x57]), name="rptr_2")

        assert len(script.pointers()) == 5
        assert script.pointers()[0] == Pointer(position=Bytes([0x00, 0x00, 0x01]), operand=Operand(Bytes([0x12, 0x34])))
        assert script.pointers()[1] == Pointer(position=Bytes([0x00, 0x00, 0x03]), operand=Operand(Bytes([0x00, 0x05])))
        assert script.pointers()[2] == Pointer(
            position=Bytes([0x00, 0x00, 0x3A]),
            anchor=Operand(Bytes([0x12, 0x00, 0x01]), variable=labels[3]),
            operand=Operand(Bytes([0x34, 0x55]), variable=labels[4]),
        )
        assert script.pointers()[3] == Pointer(
            position=Bytes([0x00, 0x00, 0x3C]),
            anchor=Operand(Bytes([0x12, 0x00, 0x01]), variable=labels[3]),
            operand=Operand(Bytes([0x34, 0x56]), variable=labels[5]),
        )
        assert script.pointers()[4] == Pointer(
            position=Bytes([0x00, 0x00, 0x3E]),
            anchor=Operand(Bytes([0x12, 0x00, 0x02])),
            operand=Operand(Bytes([0x34, 0x55]), variable=labels[5]),
        )

        assert len(script.instructions()) == 12
        assert script.instructions()[0] == Instruction(
            position=Bytes([0x00, 0x00, 0x05]), opcode=Bytes([0xAA]), operands=None
        )
        assert script.instructions()[1] == Instruction(
            position=Bytes([0x00, 0x00, 0x06]),
            opcode=Bytes([0xA1]),
            operands=[Operand(TEST_BYTE, "(_,X)", variable=ALFA)],
        )
        assert script.instructions()[2] == Instruction(
            position=Bytes([0x00, 0x00, 0x08]), opcode=Bytes([0xA2]), operands=[Operand(Bytes([0xFE, 0xDC]), "#_")]
        )

        assert script.instructions()[3] == Instruction(
            position=Bytes([0x00, 0x00, 0x0B]), opcode=Bytes([0xC2]), operands=[Operand(Bytes([0x30]), "#_")]
        )
        assert script.instructions()[4] == Instruction(
            position=Bytes([0x00, 0x00, 0x0D]),
            opcode=Bytes([0xA9]),
            operands=[Operand(Bytes([0x12, 0x34]), "#_", variable=BRAVO)],
        )
        assert script.instructions()[5] == Instruction(
            position=Bytes([0x00, 0x00, 0x10]), opcode=Bytes([0xA2]), operands=[Operand(Bytes([0xFE, 0xDC]), "#_")]
        )

        assert script.instructions()[6] == Instruction(
            position=Bytes([0x00, 0x00, 0x13]), opcode=Bytes([0xE2]), operands=[Operand(Bytes([0x30]), "#_")]
        )
        assert script.instructions()[7] == Instruction(
            position=Bytes([0x00, 0x00, 0x15]),
            opcode=Bytes([0xA9]),
            operands=[Operand(Bytes([0xC0]), "#_", variable=labels[2])],
        )
        assert script.instructions()[8] == Instruction(
            position=Bytes([0x00, 0x00, 0x17]), opcode=Bytes([0xA2]), operands=[Operand(Bytes([0xCC]), "#_")]
        )

        assert script.instructions()[9] == Instruction(
            position=Bytes([0x00, 0x00, 0x19]),
            opcode=Bytes([0x44]),
            operands=[Operand(Bytes([0x34]), "#_"), Operand(Bytes([0x12]), "#_", variable=ALFA)],
        )
        assert script.instructions()[10] == Instruction(
            position=Bytes([0x00, 0x00, 0x1C]),
            opcode=Bytes([0x4C]),
            operands=[
                Operand(
                    Bytes([0x00, 0x05]), "_", OperandType.JUMPING, Label(value=Bytes([0x00, 0x00, 0x05]), name="archie")
                )
            ],
        )
        assert script.instructions()[11] == Instruction(
            position=Bytes([0x00, 0x00, 0x1F]),
            opcode=Bytes([0x80]),
            operands=[
                Operand(Bytes([0xE0]), "_", OperandType.BRANCHING, Label(value=Bytes([0x00, 0x00, 0x01]), name="start"))
            ],
        )

        for blob in script.blobs():
            print(blob)

        assert len(script.blobs()) == 3

        assert script.blobs()[0] == Blob(position=Bytes([0x00, 0x00, 0x21]), operand=Operand(TEST_WORD, variable=BRAVO))
        assert script.blobs()[1] == Blob(
            position=Bytes([0x00, 0x00, 0x23]), operand=Operand(Bytes([0x56, 0x78])), delimiter=Operand(Bytes([0xFF]))
        )
        assert script.blobs()[2] == Blob(
            position=Bytes([0x00, 0x00, 0x26]),
            operand=Operand(Bytes([0xAB, 0xCD])),
            delimiter=Operand(Bytes([0x00]), variable=SimpleVar(Bytes.from_int(0), "delta")),
        )

        assert len(script.strings()) == 2
        assert script.strings()[0] == String(
            position=Bytes([0x00, 0x00, 0x29]),
            operand=Operand(Bytes([0x00, 0x80, 0xD8, 0xFF], endian=Endian.BIG)),
            delimiter=Operand(Bytes([0x88])),
        )
        assert script.strings()[1] == String(
            position=Bytes([0x00, 0x00, 0x34]),
            operand=Operand(Bytes([0x81, 0xA8, 0x9B, 0x01, 0xDC], endian=Endian.BIG)),
            delimiter=Operand(Bytes([0x00])),
            string_type=StringTypes.DESCRIPTION,
        )

        assert len(script.arrays()) == 1
        assert len(script.arrays()[0].parts) == 4
        assert script.arrays()[0].parts[0] == Blob(position=Bytes([0x00, 0x00, 0x2E]), operand=Operand(Bytes([0xAA])))
        assert script.arrays()[0].parts[1] == String(position=Bytes([0x00, 0x00, 0x2F]), operand=Operand(Bytes([0x9A])))
        assert script.arrays()[0].parts[2] == Blob(
            position=Bytes([0x00, 0x00, 0x30]), operand=Operand(Bytes([0xBB])), delimiter=Operand(Bytes([0xFF]))
        )

        # assert len(script.flags()) == 2

    def test_from_script_file_raises_error_when_line_is_unrecognized(self):
        with pytest.raises(UnrecognizedLine) as e:
            Script.from_text_files(DUMMY_ERROR_SCRIPT)
        assert "is not recognized." in str(e.value)

    def test_from_script_files_raises_error_when_lines_conflict(self):
        with pytest.raises(LineConflict):
            Script.from_text_files(CONFLICTING_LINES_SCRIPT)

    def test_from_script_files_raises_error_when_flags_conflict(self):
        with pytest.raises(LineConflict):
            Script.from_text_files(CONFLICTING_FLAGS_SCRIPT)

    def test_from_script_files_raises_error_when_lines_conflict_in_multiple_files(self):
        with pytest.raises(LineConflict):
            Script.from_text_files(CONFLICTING_FILE_1, CONFLICTING_FILE_2)

    def test_to_rom(self):
        with open(DUMMY_OUTPUT_ROM, "wb") as f:
            f.write(b"\x00")

        ScriptImpl().script.to_rom(output_path=DUMMY_OUTPUT_ROM)
        with open(DUMMY_OUTPUT_ROM, "rb") as f:
            output = f.read()

        assert output[0x00:0x01] == b"\x00"  # Padding
        assert output[0x01:0x03] == b"\x34\x12"  # ptr !label_c01234
        assert output[0x03:0x05] == b"\x05\x00"  # ptr !archie
        assert output[0x05:0x06] == b"\xaa"  # TAX
        assert output[0x06:0x08] == b"\xa1\x12"  # LDA (alfa,X)
        assert output[0x08:0x0B] == b"\xa2\xdc\xfe"  # LDX #$FEDC
        assert output[0x0B:0x0D] == b"\xc2\x30"  # REP #$30
        assert output[0x0D:0x10] == b"\xa9\x34\x12"  # LDA #bravo
        assert output[0x10:0x13] == b"\xa2\xdc\xfe"  # LDX #!label_c0fedc
        assert output[0x13:0x15] == b"\xe2\x30"  # SEP #$30
        assert output[0x15:0x17] == b"\xa9\xc0"  # LDA #.label_c0fedc
        assert output[0x17:0x19] == b"\xa2\xcc"  # LDX #$CC
        assert output[0x19:0x1C] == b"\x44\x34\x12"  # MVP #$34,#alfa
        assert output[0x1C:0x1F] == b"\x4c\x05\x00"  # JMP !archie
        assert output[0x1F:0x21] == b"\x80\xe0"  # BRA start
        assert output[0x21:0x23] == b"\x34\x12"  # bravo
        assert output[0x23:0x26] == b"\x78\x56\xff"  # $5678,$FF
        assert output[0x26:0x29] == b"\xcd\xab\x00"  # $ABCD,delta
        assert output[0x29:0x2E] == b"\x00\x80\xd8\xff\x88"  # "<0x00>A<KNIFE>_",$88
        assert output[0x2E:0x34] == b"\xaa\x9a\xbb\xff\x9b\x00"  # $AA | "a" | $BB,$FF | "b",$00
        assert output[0x34:0x3A] == b"\x81\xa8\x9b\x01\xdc\x00"  # desc "Bob<LINE><FIRE>",$00
        assert output[0x3A:0x3C] == b"\x55\x34"  # rptr !label_d23456
        assert output[0x3C:0x3E] == b"\x56\x34"  # rptr !label_d23457
        assert output[0x3E:0x40] == b"\x55\x34"  # rptr !label_d23457

    def test_from_rom(self):
        sections = [
            ScriptSection(start=0x000001, end=0x000005, mode=ScriptMode.POINTERS),
            ScriptSection(start=0x000005, end=0x000021, mode=ScriptMode.INSTRUCTIONS, flags=Flags(m=8)),
            ScriptSection(start=0x000021, end=0x000023, mode=ScriptMode.BLOBS, length=2),
            ScriptSection(start=0x000023, end=0x000026, mode=ScriptMode.BLOBS, delimiter=b"\xff"),
            ScriptSection(start=0x000026, end=0x000029, mode=ScriptMode.BLOBS, delimiter=b"\x00"),
            ScriptSection(
                start=0x000029,
                end=0x00002E,
                mode=ScriptMode.MENU_STRINGS,
                delimiter=b"\x88",
                charset=Charset(charset=MENU_CHARSET),
            ),
            ScriptSection(
                start=0x00002E,
                end=0x000034,
                mode=ScriptMode.ARRAYS,
                sub_sections=[
                    SubSection(mode=ScriptMode.BLOBS, length=1),
                    SubSection(mode=ScriptMode.MENU_STRINGS, length=1),
                    SubSection(mode=ScriptMode.BLOBS, delimiter=Bytes([0xFF])),
                    SubSection(mode=ScriptMode.MENU_STRINGS, delimiter=Bytes([0x00])),
                ],
            ),
            ScriptSection(
                start=0x000034,
                end=0x00003A,
                mode=ScriptMode.DESCRIPTION_STRINGS,
                delimiter=b"\x00",
                charset=Charset(charset=DESCRIPTION_CHARSET),
            ),
            ScriptSection(start=0x00003A, end=0x00003E, mode=ScriptMode.POINTERS, anchor=0x120001),
            ScriptSection(start=0x00003E, end=0x000040, mode=ScriptMode.POINTERS, anchor=0x120002),
        ]

        test_script = ScriptImpl().script

        script = Script.from_rom(filename=DUMMY_INPUT_ROM, sections=sections)

        assert len(script.pointers()) == len(test_script.pointers())

        for i in range(len(script.pointers())):
            assert script.pointers()[i].position == test_script.pointers()[i].position
            assert script.pointers()[i].operand.value == test_script.pointers()[i].operand.value

        assert len(script.instructions()) == len(test_script.instructions())
        for i in range(len(script.instructions())):
            assert script.instructions()[i].position == test_script.instructions()[i].position
            assert script.instructions()[i].opcode == test_script.instructions()[i].opcode
            if test_script.instructions()[i].operands:
                assert len(script.instructions()[i].operands) == len(test_script.instructions()[i].operands)
                for j in range(len(test_script.instructions()[i].operands)):
                    assert script.instructions()[i].operands[j].value == test_script.instructions()[i].operands[j].value

        assert len(script.blobs()) == len(test_script.blobs())
        for i in range(len(script.blobs())):
            assert script.blobs()[i].position == test_script.blobs()[i].position
            assert script.blobs()[i].operand.value == test_script.blobs()[i].operand.value

        assert len(script.strings()) == len(test_script.strings())
        for i in range(len(script.strings())):
            assert script.strings()[i].position == test_script.strings()[i].position
            assert script.strings()[i].operand.value == test_script.strings()[i].operand.value

        test_labels = [LABELS[0], LABELS[1], LABELS[2], LABELS[4], Label(pos(0x120002)), LABELS[5], LABELS[6]]

        assert len(script.labels()) == len(test_labels)
        for i in range(len(script.labels())):
            assert script.labels()[i].value == test_labels[i].value

        assert len(script.arrays()) == len(test_script.arrays())
        for i in range(len(script.arrays())):
            assert len(script.arrays()[i].parts) == len(test_script.arrays()[i].parts)
            for j in range(len(script.arrays()[i].parts)):
                assert script.arrays()[i].parts[j].operand == test_script.arrays()[i].parts[j].operand
                assert script.arrays()[i].parts[j].delimiter == test_script.arrays()[i].parts[j].delimiter
                if script.arrays()[i].parts[j].delimiter:
                    assert (
                        script.arrays()[i].parts[j].delimiter.value == test_script.arrays()[i].parts[j].delimiter.value
                    )

    def test_to_script_file(self):
        ScriptImpl().script.to_text_file(filename=DUMMY_OUTPUT_SCRIPT)
        with open(DUMMY_OUTPUT_SCRIPT) as f:
            script = f.read()
        assert script == (
            """m = 8, x = 16
db alfa = $12
dw bravo = $1234
db delta = $00

@start = $C00001
  ptr $1234
  ptr $0005
@archie
  TAX
  LDA (alfa,X)
  LDX #$FEDC
  REP #$30
  LDA #bravo
  LDX #$FEDC
  SEP #$30
  LDA #.label_c0fedc
  LDX #$CC
  MVP #$34,#alfa
  JMP !archie
  BRA start
  bravo
  $5678,$FF
  $ABCD,delta
  "<0x00>A<KNIFE>_",$88
  $AA | "a" | $BB,$FF | "b",$00
  desc "Bob<LINE><FIRE>",$00

#anchor_1
  rptr !rptr_1
  rptr !rptr_2

#$D20002
  rptr !rptr_2

@label_c0fedc = $C0FEDC

@anchor_1 = $D20001

@rptr_1 = $D23456

@rptr_2 = $D23457"""
        )
