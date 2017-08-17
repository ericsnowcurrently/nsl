import contextlib
import importlib
import os.path
import sys
import tempfile
import unittest

from nsl.importlib import copy_module, load_from_source


# XXX Move helpers to nsl.testing and nsl.workspace?

def create_temp_module(testcase, name, source):
    if not name.isidentifier():
        raise ValueError('invalid module name {!r}'.format(name))
    if name in sys.modules:
        raise RuntimeError('module {!r} already exists'.format(name))

    filename = _create_module_file(testcase, name + '.py', source)
    with _sys_path_0(os.path.dirname(filename)):
        module = importlib.import_module(name)
    testcase.addCleanup(lambda: sys.modules.pop(name))
    return module


def _create_module_file(testcase, name, content):
    tmpdir = tempfile.TemporaryDirectory(prefix='test_importlib_')
    testcase.addCleanup(tmpdir.cleanup)
    filename = os.path.join(tmpdir.name, name)
    with open(filename, 'w') as outfile:
        outfile.write(content)
    return filename


@contextlib.contextmanager
def _sys_path_0(dirname):
    sys.path.insert(0, dirname)
    try:
        yield
    finally:
        sys.path.pop(0)  # This *could* break, but it's unlikely.


class OneOffImportTests(unittest.TestCase):

    def test_copy_module_with_module(self):
        orig = create_temp_module(self, 'copy_module_test', 'x = 1')
        copied = copy_module(orig)
        copied.x = 2

        self.assertIsNot(copied, orig)
        self.assertEqual(copied.__spec__, orig.__spec__)
        self.assertIs(sys.modules['copy_module_test'], orig)
        self.assertEqual(orig.x, 1)
        self.assertEqual(copied.x, 2)

    def test_copy_module_with_string(self):
        orig = create_temp_module(self, 'copy_module_test', 'x = 1')
        copied = copy_module('copy_module_test')
        copied.x = 2

        self.assertIsNot(copied, orig)
        self.assertEqual(copied.__spec__, orig.__spec__)
        self.assertIs(sys.modules['copy_module_test'], orig)
        self.assertEqual(orig.x, 1)
        self.assertEqual(copied.x, 2)

    def test_load_from_source(self):
        orig = create_temp_module(self, 'load_from_source_test', 'x = 1')
        loaded = load_from_source('load_from_source_test', orig.__file__)
        loaded.x = 2

        self.assertIsNot(loaded, orig)
        self.assertEqual(loaded.__spec__, orig.__spec__)
        self.assertIs(sys.modules['load_from_source_test'], orig)
        self.assertEqual(orig.x, 1)
        self.assertEqual(loaded.x, 2)
