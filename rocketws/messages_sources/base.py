# -*- coding: utf-8 -*-
import collections

from gevent import Greenlet
import logging
import abc

logger = logging.getLogger('ms')


class BaseMessagesSource(object):

    """Base class for messages source.
    For subclassing it do override `_run` method.
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
        super(BaseMessagesSource, self).__init__()
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


class BaseMessagesSourceAsync(Greenlet, BaseMessagesSource):

    """Base class for messages source.
    For subclassing it do override `_run` method.
    """

    def __init__(self, on_message_callback, *args, **kwargs):
        """

        :param on_message_callback: function which expect one argument:
            def on_message_callback(raw_message):
                pass

        :param args:
        :param kwargs:
        :raise ValueError:
        """
        Greenlet.__init__(self)
        BaseMessagesSource.__init__(self, on_message_callback, *args, **kwargs)
        if not isinstance(on_message_callback, collections.Callable):
            raise ValueError(
                'on_message_callback must be a function like '
                '`def x(raw_message): ...`'
            )

        # on_message_callback must be a function like `def x(raw_message)`
        self.on_message_callback = on_message_callback

    def _run(self, *args, **kwargs):
        """

        :param args:
        :param kwargs: init `**kwargs` goes here
        :raise NotImplementedError:
        """
        raise NotImplementedError(
            '{} is not implemented `_run` method'.format(
                self.__class__.__name__))

    def stop(self):
        self.kill()
        logger.debug('MessageSource is stopped')
