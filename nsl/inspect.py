import inspect


__all__ = [
        'get_caller_module',
        ]


def get_caller_module(called=None, *, external=True):
    """Return the name of the caller's module.

    When this is called, it walks up the call stack starting with
    the caller of the function ("called") that called
    get_caller_module().  If external is False then that caller's
    module name is returned.  Otherwise it keeps walking up the stack
    until the module is different from the original one and returns
    that name.

    Knowing the module of the caller is useful in a variety of
    situations, including debugging, logging, and building classes
    dynamically.

    Note that None will be returned if there is no caller (e.g. called
    from __main__ or module body).  None is also the result if no
    "called" frame is provided (the default) and the Python
    implementation does not support frames.
    """
    if called is None:
        called = inspect.currentframe()
        if called is None:
            return None
        # Start with the frame of the get_caller_module() caller,
        # since that's our actual starting point.
        called = called.f_back

    caller = called.f_back
    if external:
        # Walk the stack.
        while caller:
            name = caller.f_globals['__name__']
            if name != called.f_globals['__name__']:
                break
            caller = caller.f_back
    if caller is None:
        return None
    return caller.f_globals['__name__']
