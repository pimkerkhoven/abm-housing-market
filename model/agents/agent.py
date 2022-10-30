import itertools


class Agent:
    id_iter = None

    def __init__(self):
        self.id = next(self.id_iter)

    def remove(self):
        print("Implement remove method for {}".format(type(self)))

    def __repr__(self):
        return "{}({})".format(type(self).__name__, self.id)

    @classmethod
    def reset_id_iter(cls):
        cls.id_iter = itertools.count()
