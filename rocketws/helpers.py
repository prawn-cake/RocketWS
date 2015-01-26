# -*- coding: utf-8 -*-
from functools import wraps
import sys
from time import time


class Singleton(type):

    """ Implement singleton pattern. """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def log_methods_time(logger=None):
    """ Decorator for log and timing execution method.

    :return func: a decorator

    """
    if not logger:
        logger = lambda _: _
        logger.debug = sys.stdout.write

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            t0 = time()
            logger.debug("timeit --> method `{}`".format(fn.__name__))
            result = fn(*args, **kwargs)
            logger.debug("timeit --> method `{}` is finished "
                         "(elapsed: {:.3f}s)".format(fn.__name__, time() - t0))
            return result
        return wrapper
    return decorator