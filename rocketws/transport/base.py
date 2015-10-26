# -*- coding: utf-8 -*-
import collections
import logging
import abc


logger = logging.getLogger('transport')


class BaseTransport(object):

    """Base class for backend transport.
    For subclassing it do override `start` method.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, on_message_callback, *args, **kwargs):
        """

        :param on_message_callback: function which expect one argument:
            def on_message_callback(raw_message):
                pass

        :param args:
        :param kwargs:
        :raise ValueError:
        """
        super(BaseTransport, self).__init__()
        if not isinstance(on_message_callback, collections.Callable):
            raise ValueError(
                'on_message_callback must be a function like '
                '`def x(raw_message): ...`'
            )

        # on_message_callback must be a function like `def x(raw_message)`
        self.on_message_callback = on_message_callback

    @abc.abstractmethod
    def start(self):
        raise NotImplementedError(
            '{} is not implemented `start` method'.format(
                self.__class__.__name__))

    @abc.abstractmethod
    def stop(self):
        raise NotImplementedError(
            '{} is not implemented `stop` method'.format(
                self.__class__.__name__))
