# -*- coding: utf-8 -*-
from collections import defaultdict
import weakref
import collections
import json
import logging
import time

from rocketws.helpers import Singleton


logger = logging.getLogger('SocketRegistry')


class SocketRegistry(object):

    """Reserved client socket registry"""

    __metaclass__ = Singleton

    def __init__(self):
        self.registry = dict()
        logger.debug('Init')

    def register(self, *clients):
        for client in clients:
            logger.debug('Register client: {}'.format(client.address))
            self.registry[client.address] = weakref.ref(client)

    def unregister(self, client):
        logger.debug('Unregister client: {}'.format(client.address))
        if client.address in self.registry:
            del self.registry[client.address]
        return True

    def get_client(self, address):
        if isinstance(address, (list, tuple)) and len(address) == 2:
            address = tuple(address)

            # NOTE: client_ref is a proxy ref here
            client_ref = self.registry.get(address)
            if client_ref is None:
                del self.registry[address]
            else:
                return client_ref()

    @property
    def clients(self):
        return self.registry.values()

    def flush(self):
        self.registry.clear()
        logger.debug('Flush registry')

    def __unicode__(self):
        return unicode(
            "{}(sockets={})".format(
                self.__class__.__name__, len(self.registry)))

    def __repr__(self):
        return unicode(
            "{}(sockets={})".format(
                self.__class__.__name__, len(self.registry)))


ch_logger = logging.getLogger('ChannelRegistry')


class ChannelRegistry(object):

    """Registry for websockets channels for clients"""

    __metaclass__ = Singleton

    MESSAGE_TYPES = {
        'broadcast': 'broadcast',
        'message': 'message'
    }

    def __init__(self, **kwargs):
        self.registry = defaultdict(list)
        ch_logger.debug('Initialized')

    def subscribe(self, channel, *clients):
        """Subscribe client for a channel.
        Method supports multiple subscriptions.

        :param channel: string channel name
        :param clients: geventwebsocket.handler.Client list
        """

        # Remove NoneType references
        active_subscribers = self._get_active_subscribers_idx(channel)

        for client in clients:
            ch_logger.debug('Subscribe client {} on channel {}'.format(
                client.address, channel))
            # Store each client as a proxy weak reference
            active_subscribers.update({client.address: weakref.proxy(client)})
        self.registry[channel] = active_subscribers.values()
        return 'subscribed'

    def unsubscribe(self, channel, *clients):
        active_subscribers = self._get_active_subscribers_idx(channel)
        for client in clients:
            ch_logger.debug('Unsubscribe client {} on channel `{}`'.format(
                client.address, channel))
            if client.address in active_subscribers:
                del active_subscribers[client.address]

        # Remove channel from registry if there are no subscribers
        if not active_subscribers:
            ch_logger.debug('There are no active subscribers for channel `{}`.'
                            'Remove it from registry.'.format(channel))
            del self.registry[channel]
        else:
            self.registry[channel] = active_subscribers.values()

        return 'unsubscribed'

    def _get_active_subscribers_idx(self, channel):
        """Get active clients idx for particular channel,
        remove NoneType references

        :param channel:
        :return: dict
        """
        active_clients_idx = {}
        # Remove NoneType references
        for c in self.registry[channel]:
            try:
                if bool(c):
                    active_clients_idx[c.address] = c
            except ReferenceError:
                continue
        return active_clients_idx

    @classmethod
    def _add_message_meta(cls, data, _type):
        """Helper method to add meta info for message

        :param data:
        :param _type:

        Meta information:
            __type  - optional message type, default is 'message'
            __ts    - message server timestamp
        """
        data.update(
            __type=cls.MESSAGE_TYPES.get(_type, 'message'),
            __ts=int(time.time())
        )

    @property
    def channels(self):
        active_channels = []
        for channel, subscribers in self.registry.items():
            try:
                all(subscribers)
            except ReferenceError:
                continue
            active_channels.append(channel)
        return active_channels

    @property
    def subscribers(self):
        """Return total subscribers for all channels

        :return: list
        """
        subscribers = []
        for channel in self.registry.keys():
            active = self._get_active_subscribers_idx(channel)
            subscribers.extend(active.values())
        return subscribers

    def get_channel_subscribers(self, channel):
        """Get alive subscribers for particular channel

        :param channel: channel name
        :return:
        """
        return self._get_active_subscribers_idx(channel).values()

    def is_client_in_channel(self, client, channel):
        """Check whether client in particular channel or not.
         NOTE: registry stores proxy object that's why simple
         `client in self.registry.get(channel)` doesn't work

        :param client:
        :param channel:
        :return:
        """
        return client.address in [
            proxy_client.address
            for proxy_client in self.registry.get(channel, [])
        ]

    def flush_channel(self, channel):
        """ Remove all data for particular channel

        :param channel:
        """
        if channel in self.registry:
            del self.registry[channel]

    def flush_all(self):
        """Clear all elements from registry

        """
        self.registry.clear()
        ch_logger.debug('Flush all')

    def flush_dead_clients(self):
        """Remove null-references for un-existed clients

        """
        count_clients = lambda: sum([len(v) for v in self.registry.values()])
        init_count = count_clients()
        for channel in self.registry.keys():
            self.registry[channel] = self._get_active_subscribers_idx(channel)
        flushed = init_count - count_clients()
        ch_logger.debug('Flush dead clients. Flushed: {}'.format(flushed))
        return {'flushed': flushed}

    def emit(self, channel, data, ignore_clients=()):
        """Emit json message for all channel clients

        :param channel: channel name
        :param data:
        :param ignore_clients: ignore clients addresses to emit data
               Example: (('127.0.0.1', 5555), )

        :raise ValueError:
        """
        ch_logger.debug(
            'Emit data `{}` for channel `{}` (ignore: {})'.format(
                data, channel, ignore_clients))
        if not isinstance(data, collections.Mapping):
            raise ValueError(
                'emit: passed data is not a dict-like: {}'.format(data))

        self._add_message_meta(data, 'message')
        serialized_data = json.dumps(data)
        subscribers = self.get_channel_subscribers(channel)

        ch_logger.debug(
            'Channel contains {} subscribers'.format(len(subscribers)))

        emitted = 0
        for client in subscribers:
            if client.address not in ignore_clients:
                client.ws.send(serialized_data)
                emitted += 1

        ch_logger.debug('Emit:ok (emitted: {})'.format(emitted))
        return 'emitted: {}'.format(emitted)

    def notify_all(self, data):
        """Notify all subscribers

        :param data:
        :return: :raise ValueError:
        """
        if not isinstance(data, collections.Mapping):
            raise ValueError(
                'notify_all: passed data is not dict-like: {}'.format(data))

        self._add_message_meta(data, 'broadcast')
        ch_logger.debug('Notify all with data {}'.format(data))
        serialized_data = json.dumps(data)

        notified = 0
        for client in self.subscribers:
            client.ws.send(serialized_data)
            notified += 1
        ch_logger.debug('Notify all:ok')

        return 'notified: {}'.format(notified)

    def __unicode__(self):
        return unicode(
            "{}(channels={}, subscribers={})".format(
                self.__class__.__name__,
                len(self.registry),
                len(self.subscribers)))

    def __repr__(self):
        return unicode(
            "{}(channels={}, subscribers={})".format(
                self.__class__.__name__,
                len(self.registry),
                len(self.subscribers)))