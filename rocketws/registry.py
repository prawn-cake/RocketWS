# -*- coding: utf-8 -*-
from rocketws.helpers import Singleton
from collections import defaultdict
from itertools import chain
import weakref


class ChannelRegistry(object):

    """Registry for websockets aliases for clients"""

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

    def unsubscribe(self, channel, client):
        active_subscribers = self._get_active_subscribers_idx(channel)
        if client.address in active_subscribers:
            del active_subscribers[client.address]
        self.registry[channel] = active_subscribers.values()

    def _get_active_subscribers_idx(self, alias):
        """Get active clients idx for particular alias,
        remove NoneType references

        :param alias:
        :return: dict
        """
        active_clients_idx = {}
        # Remove NoneType references
        for c in self.registry[alias]:
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

    def get_channel_subscribers(self, alias):
        return self._get_active_subscribers_idx(alias).values()

    def flush_channel(self, channel):
        """ Remove all data for particular alias

        :param channel:
        """
        if channel in self.registry:
            del self.registry[channel]

    def flush_all(self):
        """Clear all elements from registry

        """
        self.registry.clear()