import logging
import sys

import nsl.inspect


def level_from_verbosity(verbosity=3, maxlevel=logging.CRITICAL):
    """Return the logging level corresponding to the given verbosity."""
    return max(1,  # 0 disables it, so we use the next lowest.
               min(maxlevel,
                   maxlevel - verbosity * 10))


def get_logger(logger=None):
    """Return the corresponding logger.

    If "logger" a string then it gets looked up normally.  If None,
    the name is pulled from the current module.
    """
    if logger is None:
        name = nsl.inspect.get_caller_module()
        logger = logging.getLogger(name)
    elif isinstance(logger, str):
        logger = logging.getLogger(logger)
    return logger


def basic_handler(stream=None, level=logging.INFO, *,
                  formatter=None, **fmt):
    """Return a logging.Handler set up for basic streaming.

    If "stream" is a filename then logging.FileHandler is used.
    Otherwise logging.StreamHandler gets used.
    """
    if stream is None:
        handler = logging.StreamHandler(sys.stdout)
    elif isinstance(stream, str):
        handler = logging.FileHandler(stream, delay=True)
    else:
        handler = logging.StreamHandler(stream)

    if level is not None:
        handler.setLevel(level)
    if fmt:
        if formatter is None:
            formatter = logging.Formatter
        handler.setFormatter(
                formatter(**fmt))
    return handler


def ensure_logger(logger=None, level=logging.INFO, *handlers, **fmt):
    """Return the logger after ensuring it has at least a basic config.

    If the logger is already configured (e.g. has handlers) then it is
    not modified at all.  If no logger is given then the name of the
    current module is used.  If no handlers are provided then a basic
    streaming handler is used.
    """
    logger = get_logger(logger)
    if logger.handlers:
        # already configured
        return logger

    # Handle the log level.
    if level is not None:
        if isinstance(level, int):
            # XXX This needs to be better.
            if level <= 0 or level > logging.CRITICAL or level % 10:
                level = level_from_verbosity(level)
        logger.setLevel(level)

    #logger.propagate = False

    # Add the handlers.
    if not handlers:
        handlers = [basic_handler(level=level, **fmt)]
    if fmt:
        fmt = logging.Formatter(**fmt)
    for handler in handlers:
        if fmt and handler.formatter is None:
            handler.setFormatter(fmt)
        logger.addHandler(handler)

    return logger
