class Meta(type):
    def __new__(mcs, name, bases, dct):
        # this just iterates through the class dict and removes
        # all the dunder methods
        mcs.members = [v for k, v in dct.items() if not k.startswith('__') and not callable(v)]
        return super().__new__(mcs, name, bases, dct)

    # giving your class an __iter__ method gives you membership checking
    # and the ability to easily convert to another iterable
    def __iter__(cls):
        yield from cls.members
