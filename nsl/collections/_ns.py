from collections import namedtuple
import functools


#################################################
# record types

# XXX Add as_namedtuple() keyword args (for defaults).
# XXX Add nt.as_subclass() classmethod.
# XXX Add nt.with_defaults() classmethod.
# XXX Support using as_namedtuple() with classes that have base classes.
# XXX Ensure pickling works right.
# XXX Add Namedtuple abstract base class.

def _update_wrapper_ns(ns, wrapped):
    # We'd use functools.update_wrapper() if it worked for classes.
    for attr in functools.WRAPPER_ASSIGNMENTS:
        try:
            ns[attr] = getattr(wrapped, attr)
        except AttributeError:
            pass


def as_namedtuple(cls, fields=None):
    """Turn a class into a namedtuple subclass."""
    if fields is None:
        # used as a class decorator
        fields = cls
        return lambda cls: as_namedtuple(cls, fields)

    if not isinstance(cls, type):
        raise ValueError('expected a class, got {!r}'.format(cls))

    name = cls.__name__

    # Build the base classes for the subclass.
    nt = namedtuple(name, fields)
    base = nt
    if cls.__init__ is not object.__init__:
        # Ensure that cls.__init__ is called in sub._make() and sub._replace().
        _make = functools.wraps(nt._make)(lambda c, it: c(*it))
        basens = {
                '__slots__': (),
                '_make': classmethod(_make),
                }
        _update_wrapper_ns(basens, nt)
        base = type(name, (base,), basens)
    bases = (cls, base)

    # Build the namespace for the subclass.
    ns = {
            '__wraps__': cls,
            '__namedtuple__': nt,
            }
    if vars(cls).get('__slots__') is not None:
        ns['__slots__'] = ()
    _update_wrapper_ns(ns, cls)
    if cls.__doc__ is None:
        ns['__doc__'] = nt.__doc__

    # Build the subclass.
    sub = type(name, bases, ns)

    return sub
