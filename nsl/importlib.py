import importlib
import importlib.util


__all__ = [
        'copy_module', 'load_from_source',
        ]


def copy_module(module):
    """Return a copy of an existing module.

    sys.modules is not changed.
    """
    if isinstance(module, str):
        module = importlib.import_module(module)
    return load_from_source(module.__name__, module.__file__)


def load_from_source(name, filename):
    """Return a module loaded from the given filename."""
    spec = importlib.util.spec_from_file_location(name, filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# XXX Add import_from_source?
