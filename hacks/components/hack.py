from glob import glob

from src.lib.game_lists import ChestType, Esper
from src.lib.structures.asm import Script, Label
from src.utils import Rom, Ips


if __name__ == "__main__":
    rom = Rom("ff3.sfc")
    for filename in glob("asm/*.asm"):
        script = Script.from_script(filename=filename)
        script.assemble(pad=True)
    for i in [0x66, 0x84, 0x86]:
        relative_address = Label.get_from_name(
            name=f"gen_act_{i:02X}", filename="asm/general_actions.asm"
        ).relative_address
        rom.general_actions[i].pointer = relative_address
    rom.dialogs[0xB86].message = "\n<SPACES: 08>Obtained the Esper\n<SPACES: 0D>«<SKILL>!»<END>"
    rom.dialogs.append("\n<SPACES: 06>Obtained the Rare Item\n<SPACES: 0B>«<RARE ITEM>!»<END>")
    rom.file[0xD613:0xD617] = b"\x4B\x0C\x0C\xFE"
    rom.save_as("test3.sfc")
    ips = Ips.compare("ff3.sfc", "test3.sfc")
    ips.save_as(filename="New Treasure Chest Options v1.0.1.ips")
    rom.treasures.randomize()
    rom.treasures[0].x = int(rom.treasures[0].x) - 2
    rom.treasures[0x0E].kind = ChestType.ESPER
    rom.treasures[0x0E].value = Esper.GOLEM
    rom.treasures[0x0F].kind = ChestType.ESPER
    rom.treasures[0x0F].value = 10
    rom.save_as("test3.sfc")
