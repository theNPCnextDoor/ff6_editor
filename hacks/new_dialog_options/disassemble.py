from src.lib.structures.asm import Script
from src.utils import Rom

if __name__ == "__main__":
    rom = Rom("ff3.smc")
    script = Script.disassemble(start=0x007FBF, last_instruction_position=0x0084E0, m=True, x=True)
    script.to_script(filename="asm/dialog.asm")
