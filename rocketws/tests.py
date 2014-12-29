# -*- coding: utf-8 -*-
import unittest
from random import randint

from rocketws.registry import AliasRegistry
from geventwebsocket.handler import Client


class AliasRegistryTestCase(unittest.TestCase):
    @classmethod
    def get_ws_client(cls, address='127.0.0.1', port=None):
        if port is None:
            port = randint(10000, 65535)
        return Client(
            address=tuple([address, port]), ws='socket object goes here')

    def setUp(self):
        self.registry = AliasRegistry()

    def test_singleton(self):
        same_registry = AliasRegistry()
        self.assertEqual(self.registry, same_registry)

    def test_add_alias(self):
        self.registry.flush_all()
        alias = 'john'
        client = self.get_ws_client()
        self.registry.add_alias(alias, client)

        self.assertEqual(len(self.registry.sessions), 1)
        registered_client = self.registry.sessions[0]
        self.assertEqual(registered_client.address, client.address)
        del client

        # Expected NoneType reference still in sessions
        self.assertEqual(len(self.registry.sessions), 1)
        self.assertEqual(len(self.registry.get_clients(alias)), 0)

        client = self.get_ws_client()
        self.registry.add_alias(alias, client)
        # Expected NoneType reference will be removed and new one will be added
        self.assertEqual(len(self.registry.sessions), 1)

    def test_add_multiple_aliases_for_one_client(self):
        self.registry.flush_all()
        client = self.get_ws_client()
        alias_1 = 'mark'
        alias_2 = 'kim'
        alias_3 = 'max'
        self.registry.add_alias(alias_1, client)
        self.registry.add_alias(alias_2, client)
        self.registry.add_alias(alias_3, client)
        self.assertEqual(len(self.registry.sessions), 3)


def run_server():
    from rocketws.server import server
    server.serve_forever()


class ServerTestCase(unittest.TestCase):
    def setUp(self):
        # self.server = Process(target=run_server)
        # self.server.start()
        # self.client = create_connection('ws://0.0.0.0:8000')
        pass

    def test_echo(self):
        from rocketws.server import server
        server.start()
        print('test')
        # self.server.terminate()
