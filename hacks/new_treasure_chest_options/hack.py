from glob import glob

from src.lib.structures.fields import Script
from src.utils import Rom, Ips

if __name__ == "__main__":
    rom = Rom("test.sfc")
    for filename in glob("asm/*.asm"):
        script = Script.from_script(filename=filename)
        script.assemble(pad=True)

    rom.save_as("test2.sfc")
    ips = Ips.compare("test.sfc", "test2.sfc")
    print(ips)
