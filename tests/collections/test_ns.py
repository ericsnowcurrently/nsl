import types
import unittest

from nsl.collections._ns import as_namedtuple


class AsNamedTupleTests(unittest.TestCase):

    def test_direct(self):
        class Point:
            """A point."""

        qualname = Point.__qualname__
        Point = as_namedtuple(Point, 'x y')
        p1 = Point(1, 2)
        p2 = Point(x=1, y=2)

        self.assertEqual(Point.__name__, 'Point')
        self.assertEqual(Point.__module__, __name__)
        self.assertEqual(Point.__qualname__, qualname)
        self.assertEqual(Point.__doc__, 'A point.')
        self.assertEqual(Point._fields, ('x', 'y'))
        self.assertIsInstance(p1, tuple)
        self.assertEqual(p1, p2)

    def test_decorator(self):
        class SpamSpamSpam:
            pass

        qualname = SpamSpamSpam.__qualname__.replace('SpamSpamSpam', 'Point')

        @as_namedtuple('x y')
        class Point:
            """A point."""

        p1 = Point(1, 2)
        p2 = Point(x=1, y=2)

        self.assertEqual(Point.__name__, 'Point')
        self.assertEqual(Point.__module__, __name__)
        self.assertEqual(Point.__qualname__, qualname)
        self.assertEqual(Point.__doc__, 'A point.')
        self.assertEqual(Point._fields, ('x', 'y'))
        self.assertIsInstance(p1, tuple)
        self.assertEqual(p1, p2)

    def test_defaults(self):
        @as_namedtuple('x y data')
        class Point:
            def __new__(cls, x, y, data=None, *, coerce=True):
                if coerce:
                    x = float(x)
                    y = float(y)
                    if data is not None:
                        data = types.MappingProxyType(dict(data))
                self = super().__new__(cls, x, y, data)
                return self

        p1 = Point(1, 2)
        p2 = Point(1, 2, {'spam': 'eggs'})
        p3 = Point(1, 2, {}, coerce=False)
        p3.data['max'] = True

        self.assertEqual(p1, (1.0, 2.0, None))
        self.assertEqual(p2, (1.0, 2.0, {'spam': 'eggs'}))
        self.assertEqual(p3, (1, 2, {'max': True}))
        with self.assertRaises(TypeError):
            p2.data['max'] = True

    def test_make_without_init(self):
        @as_namedtuple('x y')
        class Point:
            pass

        p1 = Point(1, 2)
        p2 = p1._replace(x=3)
        p3 = Point._make((-5, -7))

        self.assertIs(Point._make.__func__,
                      Point.__namedtuple__._make.__func__)
        self.assertEqual(p1, (1, 2))
        self.assertEqual(p2, (3, 2))
        self.assertEqual(p3, (-5, -7))

    def test_make_with_init(self):
        called = 0

        @as_namedtuple('x y')
        class Point:
            def __init__(self, *args, **kwargs):
                nonlocal called
                called += 1

        p1 = Point(1, 2)
        p2 = p1._replace(x=3)
        p3 = Point._make((-5, -7))

        self.assertEqual(called, 3)
        self.assertIsNot(Point._make, Point.__namedtuple__._make)
        self.assertEqual(p1, (1, 2))
        self.assertEqual(p2, (3, 2))
        self.assertEqual(p3, (-5, -7))

    def test_wraps(self):
        class Point:
            """A point."""

        orig = Point
        Point = as_namedtuple(Point, 'x y')
        base0, base1 = Point.__bases__

        self.assertIs(Point.__wraps__, orig)
        self.assertIs(Point.__wraps__, base0)
        self.assertIs(Point.__namedtuple__, base1)

    def test_without_slots(self):
        @as_namedtuple('x y')
        class Point:
            pass

        p = Point(1, 2)
        p.z = 3

        self.assertEqual(Point.__slots__, ())

    def test_with_slots(self):
        @as_namedtuple('x y')
        class Point:
            __slots__ = ()

        p = Point(1, 2)

        self.assertEqual(Point.__slots__, ())
        with self.assertRaises(AttributeError):
            p.z = 3

    def test_inherit_attrs(self):
        @as_namedtuple('x y')
        class Point:
            """A point."""
            __name__ = 'XXX'
            __module__ = 'spam'
            __qualname__ = 'eggs'

        self.assertEqual(Point.__name__, 'Point')
        self.assertEqual(Point.__module__, 'spam')
        self.assertEqual(Point.__qualname__, 'eggs')
        self.assertEqual(Point.__doc__, 'A point.')
        self.assertNotEqual(Point.__doc__, Point.__namedtuple__.__doc__)

    def test_default_doc(self):
        @as_namedtuple('x y')
        class Point:
            pass

        self.assertEqual(Point.__doc__, Point.__namedtuple__.__doc__)
