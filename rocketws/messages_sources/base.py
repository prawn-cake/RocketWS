# -*- coding: utf-8 -*-
from gevent import Greenlet


class BaseMessagesSource(Greenlet):

    """Base class for messages source.
    For subclassing it do override `_run` method.
    """

    def _run(self):
        raise NotImplementedError(
            '{} is not implemented `_run` method'.format(
                self.__class__.__name__))
