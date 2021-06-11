

class Binary:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = _Binary(*args, **kwargs)
        return cls._instance


class _Binary:

    def __init__(self, binary):
        self.binary = binary

    def __get__(self, instance, owner):
        return self.binary

