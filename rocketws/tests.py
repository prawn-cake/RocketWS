# -*- coding: utf-8 -*-
import unittest
from random import randint

from rocketws.registry import ChannelRegistry
from geventwebsocket.handler import Client


class ChannelRegistryTestCase(unittest.TestCase):
    @classmethod
    def get_ws_client(cls, address='127.0.0.1', port=None):
        if port is None:
            port = randint(10000, 65535)
        return Client(
            address=tuple([address, port]), ws='socket object goes here')

    def setUp(self):
        self.registry = ChannelRegistry()

    def test_singleton(self):
        same_registry = ChannelRegistry()
        self.assertEqual(self.registry, same_registry)

    def test_subscribe(self):
        self.registry.flush_all()
        channel = 'john'
        client = self.get_ws_client()
        self.registry.subscribe(channel, client)

        self.assertEqual(len(self.registry.subscribers), 1)
        registered_client = self.registry.subscribers[0]
        self.assertEqual(registered_client.address, client.address)
        del client

        # Expected NoneType reference still in sessions
        self.assertEqual(len(self.registry.subscribers), 1)
        self.assertEqual(
            len(self.registry.get_channel_subscribers(channel)), 0)

        client = self.get_ws_client()
        self.registry.subscribe(channel, client)
        # Expected NoneType reference will be removed and new one will be added
        self.assertEqual(len(self.registry.subscribers), 1)

    def test_subscribe_on_multiple_channels(self):
        self.registry.flush_all()
        client = self.get_ws_client()
        channel_1 = 'mark'
        channel_2 = 'kim'
        channel_3 = 'max'
        self.registry.subscribe(channel_1, client)
        self.registry.subscribe(channel_2, client)
        self.registry.subscribe(channel_3, client)
        self.assertEqual(len(self.registry.subscribers), 3)

    def test_subscribe_multiple_clients_for_one_channel(self):
        self.registry.flush_all()
        channel = 'chat'
        client_1 = self.get_ws_client()
        client_2 = self.get_ws_client()
        client_3 = self.get_ws_client()
        self.registry.subscribe(channel, client_1)
        self.registry.subscribe(channel, client_2)
        self.registry.subscribe(channel, client_3)

        # Expect {<channel>: [client_1, client_2, client_3]} storage
        self.assertEqual(len(self.registry.subscribers), 3)
        self.assertEqual(
            len(self.registry.get_channel_subscribers(channel)), 3)


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
