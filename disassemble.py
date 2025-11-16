import tomllib

from src.lib.structures.asm.flags import Flags
from src.lib.structures.asm.script import Script, ScriptSection, ScriptMode, SubSection


def disassemble(configs: dict):
    sections = []
    for el in configs["sections"]:
        section = ScriptSection(
            start=el["start"],
            end=el["end"],
            mode=getattr(ScriptMode, el["mode"]),
            length=el.get("length", None),
            delimiter=el.get("delimiter", None),
        )
        flags = el.get("flags", None)

        if flags:
            section.attributes["flags"] = Flags(m=flags["m"], x=flags["x"])

        elements = el.get("subsections", list())
        subsections = list()
        for s in elements:
            subsection = SubSection(
                mode=getattr(ScriptMode, s["mode"]), length=s.get("length", None), delimiter=s.get("delimiter", None)
            )
            subsections.append(subsection)

        sections.append(section)

    sections.sort()
    flags = Flags()
    for section in sections:
        if section.attributes.get("flags", None):
            flags = section.attributes["flags"]

    script = Script.from_rom(filename=configs["source"], sections=sections)
    script.to_script_file(filename=configs["destination"], flags=flags, debug=configs.get("debug", False))


if __name__ == "__main__":
    with open("config.toml") as f:
        configs = tomllib.loads(f.read())["disassembly"]
    disassemble(configs)
