# -*- coding: utf-8 -*-
from pushup.helpers import Singleton
from collections import defaultdict
from itertools import chain


class ClientsRegistry(object):

    """Registry for websockets clients"""

    __metaclass__ = Singleton

    def __init__(self, **kwargs):
        self.registry = dict()
        self.registry_alias = defaultdict(list)

    def register(self, client):
        _id = client.address
        self.registry[_id] = client

    def register_alias(self, alias, client):
        if client.address in self.registry:
            self.registry_alias[alias].append(client)
            tmp = {c.address: c for c in self.registry_alias[alias]}
            tmp.update({client.address: client})
            self.registry_alias[alias] = tmp.values()
        else:
            # TODO: log warning, impossible to register alias without main register entry
            pass

    def unregister(self, client):
        if client.address in self.registry:
            del self.registry[client.address]
            # FIXME: remove alias

    def unregister_alias(self, alias, client):
        if alias in self.registry_alias:
            self.registry_alias[alias] = [
                c for c in self.registry_alias[alias]
                if client.address != c.address
            ]
            if not self.registry_alias[alias]:
                del self.registry_alias[alias]

    @property
    def clients(self):
        return self.registry.keys()

    @property
    def sessions(self):
        return list(chain(*self.registry_alias.values()))