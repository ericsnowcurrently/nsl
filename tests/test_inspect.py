import types
import unittest

import nsl.importlib
from nsl.inspect import get_caller_module


class StubFrame:

    @classmethod
    def stack(cls, *modules):
        frame = None
        for module in reversed(modules):
            frame = cls(module, frame)
        return frame

    def __init__(self, module, parent=None):
        self.f_globals = {
                '__name__': module,
                }
        self.f_back = parent


class GetCallerModuleTests(unittest.TestCase):

    def test_defaults(self):
        called = StubFrame.stack('x', 'x', 'y', 'z')
        module = get_caller_module(called)

        self.assertEqual(module, 'y')

    def test_full_defaults(self):
        module = get_caller_module()

        self.assertEqual(module, 'unittest.case')

    def test_frames_not_supported(self):
        # Avoid modifying the real nsl.inspect while monkeypatching.
        copied = nsl.importlib.copy_module('nsl.inspect')
        copied.inspect = types.SimpleNamespace(currentframe=lambda: None)
        get_caller_module = copied.get_caller_module

        module = get_caller_module()

        self.assertIsNone(module)

    def test_no_caller(self):
        called = StubFrame.stack('x', 'x', 'x')
        module = get_caller_module(called)

        self.assertIsNone(module)

    def test_not_external_has_caller(self):
        called = StubFrame.stack('x', 'x', 'y', 'z')
        module = get_caller_module(called, external=False)

        self.assertEqual(module, 'x')

    def test_not_external_no_caller(self):
        called = StubFrame.stack('x')
        module = get_caller_module(called, external=False)

        self.assertIsNone(module)
