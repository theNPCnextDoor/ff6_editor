from src.lib.structures.asm.flags import Flags, RegisterWidth
from src.lib.structures.asm.script import ScriptSection, ScriptMode, Script, SubSection

if __name__ == "__main__":
    flags = Flags(m=RegisterWidth.EIGHT_BITS)
    sections = [
        ScriptSection(start=0x0304E0, end=0x0304F9, mode=ScriptMode.INSTRUCTIONS, flags=flags),
#         # ScriptSection(start=0x0361A2, end=0x0361B2, mode=ScriptMode.INSTRUCTIONS, flags=flags),
#         # ScriptSection(start=0x030C6C, end=0x030CEF, mode=ScriptMode.INSTRUCTIONS, flags=flags)
#         # # Pointer to initialize menu.
#         # ScriptSection(start=0x03332D, end=0x033337, mode=ScriptMode.BLOBS, length = 2 ),
#         # # Root instructions
#         # ScriptSection(start=0x031C46, end=0x031C5D, mode=ScriptMode.INSTRUCTIONS, flags=flags),
#         # # Multiple instructions
#         # ScriptSection(start=0x035D05, end=0x035D77, mode=ScriptMode.INSTRUCTIONS, flags=flags),
#         # # Blobs
#         # ScriptSection(
#         #     start=0x035F79,
#         #     end=0x035F8D,
#         #     mode=ScriptMode.BLOB_GROUPS,
#         #     sub_sections=[SubSection(mode=ScriptMode.BLOBS, length=2), SubSection(mode=ScriptMode.BLOBS, length=2)],
#         # ),
#         # # Multiple instructions
#         # ScriptSection(start=0x035FC2, end=0x036096, mode=ScriptMode.INSTRUCTIONS, flags=flags),
#         # # Blobs
#         # ScriptSection(start=0x036096, end=0x0360A0, mode=ScriptMode.BLOBS, length=2),
#         # # Set to condense BG3 text in Status menu
#         # ScriptSection(start=0x03620B, end=0x03622A, mode=ScriptMode.INSTRUCTIONS, flags=flags),
#         # # Lines vertical offset?
#         # ScriptSection(
#         #     start=0x03622A,
#         #     end=0x03625B,
#         #     mode=ScriptMode.BLOB_GROUPS,
#         #     sub_sections=[
#         #         SubSection(mode=ScriptMode.BLOBS, length=1),
#         #         SubSection(mode=ScriptMode.BLOBS, length=1),
#         #         SubSection(mode=ScriptMode.BLOBS, length=1),
#         #     ],
#         # ),
#         # ScriptSection(start=0x036437, end=0x03646F, mode=ScriptMode.POINTERS),
#         # ScriptSection(
#         #     start=0x03646F,
#         #     end=0x03652D,
#         #     mode=ScriptMode.BLOB_GROUPS,
#         #     sub_sections=[
#         #         SubSection(mode=ScriptMode.BLOBS, length=2),
#         #         SubSection(mode=ScriptMode.MENU_STRINGS, delimiter=b"\x00"),
#              ],
#          ),
    ]
    script = Script.from_rom(filename="ff3.smc", sections=sections)
    script.to_script_file("asm/status_page_2.asm", flags=flags)

# if __name__ == "__main__":
#     script = Script.from_script_file(filename="asm/earring.asm")
#     script.to_script_file(filename="asm/earring2.asm", flags=Flags())
