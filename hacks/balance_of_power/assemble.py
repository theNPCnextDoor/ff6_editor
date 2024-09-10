from glob import glob

from src.lib.structures.asm import Script
from src.utils import Rom

if __name__ == "__main__":
    rom = Rom("ff3.smc")
    for filename in glob("asm/*.asm"):
        script = Script.from_script(filename=filename)
        script.assemble(pad=True)
    rom.save_as("test.sfc")