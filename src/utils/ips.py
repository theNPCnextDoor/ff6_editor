from src.lib.structures.fields import Bytes


class Ips:

    def __init__(self, differences):
        self.differences = differences

    @classmethod
    def compare(cls, original_filename, destination_filename):
        with open(original_filename, "rb") as original_rom:
            original_bytes = original_rom.read()
        with open(destination_filename, "rb") as destination_rom:
            destination_bytes = destination_rom.read()
        file_size = min(len(original_bytes), len(destination_bytes), 3 * 1024 * 1024)
        in_a_streak = False
        differences = []
        for i in range(file_size):
            if original_bytes[i] != destination_bytes[i]:
                if in_a_streak:
                    differences[-1][1].append(destination_bytes[i])
                    differences[-1][2].append(original_bytes[i])
                else:
                    in_a_streak = True
                    differences.append([
                        Bytes(value=i, length=3, endianness="big"),
                        Bytes(destination_bytes[i], length=1, endianness="big"),
                        Bytes(original_bytes[i], length=1, endianness="big")]
                    )
            else:
                in_a_streak = False
        return cls(differences)

    def to_bytes(self, anti_patch=False, compress=False):
        output = b'PATCH'
        for difference in self.differences:
            output += bytes(difference[0])
            if anti_patch:
                payload = difference[2]
            else:
                payload = difference[1]
            output += bytes(Bytes(value=len(payload), length=2, endianness="big"))
            output += bytes(payload)
        output += b'EOF'
        return output

    def __str__(self):
        output = ""
        for difference in self.differences:
            output += (
                f"{difference[0].to_address()}-{(difference[0] + len(difference[1]) - 1).to_address()}: "
                f"{difference[1]} | {difference[2]}\n"
            )
        return output

    def save(self, filename: str, anti_patch: bool = False, compress: bool = False):
        with open(filename, "wb") as f:
            f.write(self.to_bytes(anti_patch=anti_patch, compress=compress))
