class Array:
    def __init__(self, cls, quantity: int):
        self.cls = cls
        self.quantity = quantity

    def __getitem__(self, item):
        return self.cls(id=item)

    def randomize(self):
        for i in range(self.quantity):
            self.cls(id=i).randomize()
