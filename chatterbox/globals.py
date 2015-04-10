class Globals:
    pass


class Proxy:

    def __init__(self, name):
        self.name = name

    def __getattr__(self, item):
        return getattr(getattr(_globals, self.name), item)


_globals = Globals()
