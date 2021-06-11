

class DialogArray:

    def __init__(self, cls, quantity: int):
        self.cls = cls
        self.quantity = quantity

    def __getitem__(self, item):
        if 0 <= item <= self.quantity:
            return self.cls(id=item)

    # def append(self, dialog):
    #     self.quantity += 1
    #
