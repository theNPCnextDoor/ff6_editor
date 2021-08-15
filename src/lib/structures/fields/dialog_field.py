from src.lib.game_lists import RomMap
from src.lib.structures import Binary, Bytes


class DialogField:
    def __get__(self, instance, owner):
        start = instance.address
        if instance.id == RomMap.DIALOG_QUANTITY:
            end = instance.end_address(start)
            message = Binary()[start:end]
            return message

        else:
            next_dialog = owner(id=instance.id + 1)
            end = next_dialog.address
            return Binary()[start:end]

    def __set__(self, instance, value):
        if type(value) == str:
            new_message = instance.dte.to_bytes(value)
        else:
            new_message = value
        if new_message[-1] != 0:
            new_message.append(0)
        compressed_messages = [new_message]
        if instance.available_space < len(new_message):
            overflow = len(new_message) - len(instance.message)
            i = 1
            while overflow > 0:
                next_dialog = instance.__class__(id=instance.id + i)
                string = next_dialog.dte.to_string(next_dialog.message)
                compressed_message = next_dialog.dte.to_bytes(string)
                compressed_messages.append(compressed_message)
                overflow = overflow - (
                    next_dialog.available_space - len(compressed_message)
                )
                i += 1
        for i, message in enumerate(compressed_messages):
            next_dialog = instance.__class__(id=instance.id + i + 1)
            current_dialog = instance.__class__(id=instance.id + i)
            if next_dialog.id <= RomMap.DIALOG_QUANTITY:
                if i < len(compressed_messages) - 1:
                    next_dialog.pointer = current_dialog.pointer + len(message)
                if next_dialog.pointer < current_dialog.pointer:
                    Binary()[
                        RomMap.DIALOG_POINTER_2ND_BANK : RomMap.DIALOG_POINTER_2ND_BANK
                        + 2
                    ] = bytes(Bytes(next_dialog.id, length=2))
            if current_dialog.address + len(message) > RomMap.DIALOG_2ND_BANK_END:
                raise IndexError(
                    f"The dialog goes over the limit {RomMap.DIALOG_2ND_BANK_END:06X}."
                )
            Binary()[
                current_dialog.address : current_dialog.address + len(message)
            ] = bytes(message)
