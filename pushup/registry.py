# -*- coding: utf-8 -*-
from pushup.helpers import Singleton
from collections import defaultdict
from itertools import chain
import weakref


class AliasRegistry(object):

    """Registry for websockets aliases for clients"""

    __metaclass__ = Singleton

    def __init__(self, **kwargs):
        self.registry = defaultdict(list)

    def add_alias(self, alias, client):
        """Add alias for existing client.
        Useful for

        :param alias: string alias
        :param client: geventwebsocket.handler.Client
        """
        # Remove NoneType references
        active_clients = self._get_active_clients_idx(alias)
        active_clients.update({client.address: weakref.proxy(client)})
        self.registry[alias] = active_clients.values()

    def _get_active_clients_idx(self, alias):
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
    def clients(self):
        return self.registry.keys()

    @property
    def sessions(self):
        # TODO: rewrite method to return only active user sessions (clients)
        return list(chain(*self.registry.values()))

    def get_clients(self, alias):
        return self._get_active_clients_idx(alias).values()

    def flush(self, alias):
        """ Remove all data for particular alias

        :param alias:
        """
        if alias in self.registry:
            del self.registry[alias]

    def flush_all(self):
        """Clear all elements from registry

        """
        self.registry.clear()