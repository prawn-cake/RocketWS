# -*- coding: utf-8 -*-
from rocketws.helpers import Singleton
from collections import defaultdict
from itertools import chain
import weakref
import collections
import json


class SocketRegistry(object):

    """Reserved client socket registry"""

    __metaclass__ = Singleton

    def __init__(self):
        self.registry = dict()

    def register(self, client):
        self.registry[client.address] = weakref.ref(client)

    def unregister(self, client):
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

    def __unicode__(self):
        return unicode(
            "{}(sockets={})".format(
                self.__class__.__name__, len(self.registry)))

    def __repr__(self):
        return unicode(
            "{}(sockets={})".format(
                self.__class__.__name__, len(self.registry)))


class ChannelRegistry(object):

    """Registry for websockets channels for clients"""

    __metaclass__ = Singleton

    def __init__(self, **kwargs):
        self.registry = defaultdict(list)

    def subscribe(self, channel, client):
        """Subscribe client for a channel

        :param channel: string channel name
        :param client: geventwebsocket.handler.Client
        """

        # Remove NoneType references
        active_subscribers = self._get_active_subscribers_idx(channel)
        # Store each client as a proxy weak reference
        active_subscribers.update({client.address: weakref.proxy(client)})
        self.registry[channel] = active_subscribers.values()
        return True

    def unsubscribe(self, channel, client):
        active_subscribers = self._get_active_subscribers_idx(channel)
        if client.address in active_subscribers:
            del active_subscribers[client.address]

        # Remove channel from registry if there are no subscribers
        if not active_subscribers:
            del self.registry[channel]
        else:
            self.registry[channel] = active_subscribers.values()

        return True

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

    @property
    def channels(self):
        return self.registry.keys()

    @property
    def subscribers(self):
        """Return total subscribers for all channels

        :return: list
        """
        # TODO: rewrite method to return only active user sessions (clients)
        return list(chain(*self.registry.values()))

    def get_channel_subscribers(self, channel):
        return self._get_active_subscribers_idx(channel).values()

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

    def emit(self, channel, data):
        """Emit json message for all channel clients

        :param channel: channel name
        :param data:
        :raise ValueError:
        """
        if not isinstance(data, collections.Hashable):
            raise ValueError(
                'emit: passed data is not hashable: {}'.format(data))

        serialized_data = json.dumps(data)
        for client in self.get_channel_subscribers(channel):
            client.ws.send(serialized_data)

        return True

    def notify_all(self, data):
        """Notify all subscribers

        :param data:
        :return: :raise ValueError:
        """
        if not isinstance(data, collections.Hashable):
            raise ValueError(
                'notify_all: passed data is not hashable: {}'.format(data))

        serialized_data = json.dumps(data)
        for client in self.subscribers:
            client.ws.send(serialized_data)

        return True

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