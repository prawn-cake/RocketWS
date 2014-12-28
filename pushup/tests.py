# -*- coding: utf-8 -*-
import unittest
from pushup.registry import ClientsRegistry
from websocket import create_connection
from multiprocessing import Process
from random import randint
from simplemodels.models import DictEmbeddedDocument
from simplemodels.fields import SimpleField


class Client(DictEmbeddedDocument):

    """Mock client"""

    address = SimpleField()
    ws = SimpleField()


class ClientsRegistryTestCase(unittest.TestCase):
    @classmethod
    def get_ws_client(cls, address='127.0.0.1', port=None):
        if port is None:
            port = randint(10000, 65535)
        return Client.get_instance(
            address=tuple([address, port]), ws='socket object goes here')

    def setUp(self):
        self.registry = ClientsRegistry()

    def test_singleton(self):
        same_registry = ClientsRegistry()
        self.assertEqual(self.registry, same_registry)

    def test_register_client(self):
        client = self.get_ws_client()
        self.registry.register(client)
        self.assertEqual(len(self.registry.clients), 1)
        self.assertEqual(len(self.registry.sessions), 0, self.registry.sessions)

    def test_register_client_alias(self):
        alias = 'john'
        client = self.get_ws_client()
        self.registry.register_alias(alias, client)  # return an error

        self.registry.register(client)
        self.registry.register_alias(alias, client)
        self.assertEqual(len(self.registry.sessions), 1)

    def test_unregister_client(self):
        client = self.get_ws_client()
        self.registry.register(client)
        self.registry.unregister(client)

    def test_unregister_client_alias(self):
        pass

    def test_register_multiple_clients_from_one_ip(self):
        pass


def run_server():
    from pushup.server import server
    server.serve_forever()


class ServerTestCase(unittest.TestCase):
    def setUp(self):
        # self.server = Process(target=run_server)
        # self.server.start()
        # self.client = create_connection('ws://0.0.0.0:8000')
        pass

    def test_echo(self):
        from pushup.server import server
        server.start()
        print('test')
        # self.server.terminate()
