

class classonly:
    """Like the builtin classmethod but does not show up on instances.

    This is an alternative to putting the methods on a metaclass.  It
    is especially meaningful for alternate constructors.

    This is a non-data descriptor.  It may be used as a decorator.

    """

    # Note that we do not subclass classmethod here.  Doing so would
    # prevent us from wrapping non-functions.

    def __init__(self, value):
        self.value = value
        try:
            get = type(value).__get__
        except AttributeError:
            self._get = lambda cls: value
        else:
            self._get = lambda cls: get(value, cls, cls)

    def __repr__(self):
        return '{}({!r})'.format(type(self).__name__, self.value)

    def __get__(self, obj, cls):
        if obj is not None:
            raise AttributeError
        return self._get(cls)


class factory(classonly):
    """A class-only method decorator to mark a factory for the class."""
