_UNRECOGNIZED_ARGS_ATTR = '_unrecognized_args'


class Parent(object):
    def __init__(self):
        pass

    def parse(self):
        vars(self).setdefault(_UNRECOGNIZED_ARGS_ATTR, [])


class Child(Parent):
    def __init__(self):
        self._cli = {}

    def parse(self):
        super(Child, self).parse()

    def __setattr__(self, name, value):
        if '_cli' not in self.__dict__:
            super(Child, self).__setattr__(name, value)
            return
        self._cli[name] = value

    def __getattr__(self, name):
        try:
            return self._cli[name]
        except KeyError:
            raise AttributeError(
                "'_Namespace' object has no attribute '%s'" % name)

    def __delattr__(self, name):
        if name == _UNRECOGNIZED_ARGS_ATTR:
            return super(Child, self).__delattr__(name)
        try:
            del self._cli[name]
        except KeyError:
            raise AttributeError(
                "'_Namespace' object has no attribute '%s'" % name)
