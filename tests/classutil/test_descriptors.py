import unittest

from nsl.classutil._descriptors import classonly


class Attr:

    def __init__(self, value):
        self.value = value

    def __get__(self, obj, cls):
        return self.value


class ClassonlyTests(unittest.TestCase):

    def test_repr(self):
        attr = classonly(42)
        attrrepr = repr(attr)

        self.assertEqual(attrrepr, 'classonly(42)')

    def test_on_method(self):
        calls = 0

        class Spam:
            @classonly
            def eggs(cls):
                nonlocal calls
                calls += 1

        Spam.eggs()
        spam = Spam()

        self.assertEqual(calls, 1)
        with self.assertRaises(AttributeError):
            spam.eggs()

    def test_on_attr(self):
        value = object()
        value = 42

        class Spam:
            eggs = classonly(value)

        eggs = Spam.eggs
        spam = Spam()

        self.assertIs(eggs, value)
        with self.assertRaises(AttributeError):
            spam.eggs

    def test_on_descriptor(self):
        value = object()

        class Spam:
            eggs = classonly(Attr(value))

        eggs = Spam.eggs
        spam = Spam()

        self.assertIs(eggs, value)
        with self.assertRaises(AttributeError):
            spam.eggs
