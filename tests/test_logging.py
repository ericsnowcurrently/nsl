import logging
import os.path
import sys
import types
import unittest

import nsl.importlib
from nsl.logging import (
        level_from_verbosity, basic_handler,
        # loaded dynamically below to avoid races:
        #get_logger, ensure_logger,
        )


def monkeypatch_nsl_logging(logging, **inspect):
    # Avoid modifying the real nsl.logging while monkeypatching.
    copied = nsl.importlib.copy_module('nsl.logging')
    copied.logging = logging
    copied.nsl = types.SimpleNamespace(
            inspect=types.SimpleNamespace(**inspect))
    return copied


class LevelFromVerbosityTests(unittest.TestCase):

    def test_defaults(self):
        level = level_from_verbosity()

        self.assertEqual(level, logging.INFO)

    def test_verbosity(self):
        tests = {
                -5: logging.CRITICAL,
                0: logging.CRITICAL,
                1: logging.ERROR,
                2: logging.WARNING,
                3: logging.INFO,
                4: logging.DEBUG,
                5: 1,
                10: 1,
                }
        for verbosity, expected in tests.items():
            with self.subTest(verbosity):
                level = level_from_verbosity(verbosity)

                self.assertEqual(level, expected)

    def test_maxlevel(self):
        tests = {
                100: 70,
                60: logging.WARNING,
                55: 25,
                logging.CRITICAL: logging.INFO,
                logging.ERROR: logging.DEBUG,
                logging.WARNING: 1,
                logging.INFO: 1,
                logging.DEBUG: 1,
                5: 1,
                1: 1,
                0: 1,
                -5: 1,
                }
        for maxlevel, expected in tests.items():
            with self.subTest(maxlevel):
                level = level_from_verbosity(3, maxlevel)

                self.assertEqual(level, expected)


class GetLoggerTests(unittest.TestCase):

    def test_defaults(self):
        logging = nsl.importlib.copy_module('logging')
        orig = logging.getLogger('spam')
        orig_ns = dict(vars(orig))
        nsl_logging = monkeypatch_nsl_logging(
                logging, get_caller_module=lambda: 'spam')
        logger = nsl_logging.get_logger()

        self.assertEqual(logger.name, 'spam')
        self.assertIs(logger, orig)
        self.assertEqual(vars(logger), orig_ns)

    def test_str(self):
        logging = nsl.importlib.copy_module('logging')
        orig = logging.getLogger('spam')
        orig_ns = dict(vars(orig))
        nsl_logging = monkeypatch_nsl_logging(logging)
        logger = nsl_logging.get_logger('spam')

        self.assertEqual(logger.name, 'spam')
        self.assertIs(logger, orig)
        self.assertEqual(vars(logger), orig_ns)

    def test_noop(self):
        logging = nsl.importlib.copy_module('logging')
        orig = logging.getLogger('spam')
        orig_ns = dict(vars(orig))
        nsl_logging = monkeypatch_nsl_logging(logging)
        logger = nsl_logging.get_logger(orig)

        self.assertIs(logger, orig)
        self.assertEqual(vars(logger), orig_ns)


class BasicHandlerTests(unittest.TestCase):

    def test_defaults(self):
        handler = basic_handler()

        self.assertIs(handler.level, logging.INFO)
        self.assertIs(type(handler), logging.StreamHandler)
        self.assertIs(handler.stream, sys.stdout)

    def test_without_stream(self):
        handler = basic_handler(stream=None)

        self.assertIs(type(handler), logging.StreamHandler)
        self.assertIs(handler.stream, sys.stdout)

    def test_with_str_stream(self):
        handler = basic_handler(stream='spam')

        self.assertIs(type(handler), logging.FileHandler)
        self.assertEqual(handler.baseFilename, os.path.abspath('spam'))

    def test_with_nonstr_stream(self):
        stream = object()
        handler = basic_handler(stream=stream)

        self.assertIs(type(handler), logging.StreamHandler)
        self.assertIs(handler.stream, stream)

    def test_without_level(self):
        handler = basic_handler(level=None)

        self.assertIs(handler.level, logging.NOTSET)

    def test_with_level(self):
        handler = basic_handler(level=100)

        self.assertEqual(handler.level, 100)

    def test_with_fmt(self):
        handler = basic_handler(fmt='{message}', datefmt='%y-%m-%d', style='{')

        self.assertIsInstance(handler.formatter._style, logging.StrFormatStyle)
        self.assertEqual(handler.formatter._fmt, '{message}')
        self.assertEqual(handler.formatter.datefmt, '%y-%m-%d')


class EnsureLoggerTests(unittest.TestCase):

    def test_defaults(self):
        logging = nsl.importlib.copy_module('logging')
        orig = logging.getLogger('spam')
        orig_ns = dict(vars(orig))
        nsl_logging = monkeypatch_nsl_logging(
                logging, get_caller_module=lambda: 'spam')
        logger = nsl_logging.ensure_logger()

        self.assertEqual(logger.name, 'spam')
        self.assertIs(logger, orig)
        self.assertNotEqual(vars(logger), orig_ns)
        self.assertEqual(logger.level, logging.INFO)
        self.assertTrue(len(logger.handlers), 1)
        self.assertIsInstance(logger.handlers[0], logging.StreamHandler)

    def test_already_initialized(self):
        logging = nsl.importlib.copy_module('logging')
        orig = logging.getLogger('spam')
        orig.addHandler(basic_handler())
        orig_ns = dict(vars(orig))
        nsl_logging = monkeypatch_nsl_logging(logging)
        logger = nsl_logging.ensure_logger(
                orig, logging.ERROR, basic_handler())

        self.assertIs(logger, orig)
        self.assertEqual(vars(logger), orig_ns)

    def test_with_level(self):
        logging = nsl.importlib.copy_module('logging')
        nsl_logging = monkeypatch_nsl_logging(logging)
        levels = [
                logging.CRITICAL,
                logging.ERROR,
                logging.WARNING,
                logging.INFO,
                logging.DEBUG,
                ]
        for level in levels:
            with self.subTest(level):
                logging.Logger.manager.loggerDict = {}
                orig = logging.getLogger('spam')
                logger = nsl_logging.ensure_logger(orig, level)

                self.assertIs(logger, orig)
                self.assertIs(logger.level, level)

    def test_with_verbosity(self):
        logging = nsl.importlib.copy_module('logging')
        nsl_logging = monkeypatch_nsl_logging(logging)
        tests = {
                0: logging.CRITICAL,
                1: logging.ERROR,
                2: logging.WARNING,
                3: logging.INFO,
                4: logging.DEBUG,
                5: 1,
                11: 1,
                21: 1,
                60: 1,
                }
        for i in range(-5, 0):
            tests[i] = logging.CRITICAL
        for i in range(6, 10):
            tests[i] = 1
        for i in range(51, 110):
            tests[i] = 1
        for verbosity, expected in tests.items():
            with self.subTest(verbosity):
                logging.Logger.manager.loggerDict = {}
                orig = logging.getLogger('spam')
                logger = nsl_logging.ensure_logger(orig, verbosity)

                self.assertIs(logger, orig)
                self.assertEqual(logger.level, expected)

    def test_without_handlers(self):
        logging = nsl.importlib.copy_module('logging')
        orig = logging.getLogger('spam')
        nsl_logging = monkeypatch_nsl_logging(logging)
        logger = nsl_logging.ensure_logger(orig, logging.ERROR)
        handler = logger.handlers[0]

        self.assertEqual(len(logger.handlers), 1)
        self.assertIs(handler.level, logging.ERROR)

    def test_with_handlers(self):
        handler1 = basic_handler()
        handler2 = basic_handler()
        logging = nsl.importlib.copy_module('logging')
        orig = logging.getLogger('spam')
        nsl_logging = monkeypatch_nsl_logging(logging)
        logger = nsl_logging.ensure_logger(
                orig, logging.INFO, handler1, handler2)

        self.assertEqual(logger.handlers, [handler1, handler2])

    def test_with_fmt_without_handlers(self):
        logging = nsl.importlib.copy_module('logging')
        orig = logging.getLogger('spam')
        nsl_logging = monkeypatch_nsl_logging(
                logging, get_caller_module=lambda: 'spam')
        logger = nsl_logging.ensure_logger(
                orig, logging.ERROR,
                fmt='{message}', datefmt='%y-%m-%d', style='{')
        formatter = logger.handlers[0].formatter

        self.assertIsInstance(formatter._style, logging.StrFormatStyle)
        self.assertEqual(formatter._fmt, '{message}')
        self.assertEqual(formatter.datefmt, '%y-%m-%d')

    def test_with_fmt_with_handlers(self):
        handler = basic_handler()
        logging = nsl.importlib.copy_module('logging')
        orig = logging.getLogger('spam')
        nsl_logging = monkeypatch_nsl_logging(logging)
        nsl_logging.ensure_logger(
                orig, logging.ERROR, handler,
                fmt='{message}', datefmt='%y-%m-%d', style='{')

        self.assertIsInstance(handler.formatter._style, logging.StrFormatStyle)
        self.assertEqual(handler.formatter._fmt, '{message}')
        self.assertEqual(handler.formatter.datefmt, '%y-%m-%d')
