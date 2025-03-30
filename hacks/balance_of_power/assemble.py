from src.lib.structures.asm.script import Script

if __name__ == "__main__":
    script = Script.from_script_file(filename="asm/status_page.asm")
    script.to_rom(output_path="test.smc", input_path="ff3.smc")