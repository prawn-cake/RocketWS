# -*- coding: utf-8 -*-
import unittest
from random import randint
from jsonrpc.jsonrpc2 import JSONRPC20Request

from rocketws.registry import ChannelRegistry, SocketRegistry
from geventwebsocket.handler import Client
from jsonrpc import JSONRPCResponseManager
from rocketws.server import dispatcher, registry
import mock


def get_ws_client(address='127.0.0.1', port=None):
    if port is None:
        port = randint(10000, 65535)
    client = Client(address=tuple([address, port]), ws=mock.MagicMock())
    client.ws.send = mock.MagicMock(return_value=True)
    return client


class ChannelRegistryTestCase(unittest.TestCase):
    def setUp(self):
        self.registry = ChannelRegistry()

    def test_singleton(self):
        same_registry = ChannelRegistry()
        self.assertEqual(self.registry, same_registry)

    def test_subscribe(self):
        self.registry.flush_all()
        channel = 'john'
        client = get_ws_client()
        self.registry.subscribe(channel, client)

        self.assertEqual(len(self.registry.subscribers), 1)
        registered_client = self.registry.subscribers[0]
        self.assertEqual(registered_client.address, client.address)
        del client

        # Expected NoneType reference still in sessions
        self.assertEqual(len(self.registry.subscribers), 1)
        self.assertEqual(
            len(self.registry.get_channel_subscribers(channel)), 0)

        client = get_ws_client()
        self.registry.subscribe(channel, client)
        # Expected NoneType reference will be removed and new one will be added
        self.assertEqual(len(self.registry.subscribers), 1)

    def test_subscribe_on_multiple_channels(self):
        self.registry.flush_all()
        client = get_ws_client()
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
        client_1 = get_ws_client()
        client_2 = get_ws_client()
        client_3 = get_ws_client()
        self.registry.subscribe(channel, client_1)
        self.registry.subscribe(channel, client_2)
        self.registry.subscribe(channel, client_3)

        # Expect {<channel>: [client_1, client_2, client_3]} storage
        self.assertEqual(len(self.registry.subscribers), 3)
        self.assertEqual(
            len(self.registry.get_channel_subscribers(channel)), 3)


class SocketRegistryTestCase(unittest.TestCase):
    def setUp(self):
        self.registry = SocketRegistry()

    def test_register(self):
        self.registry.flush()
        client = get_ws_client()
        self.registry.register(client)
        self.assertEqual(len(self.registry.clients), 1, self.registry.clients)

    def test_unregister(self):
        self.registry.flush()
        client = get_ws_client()
        self.registry.register(client)
        self.registry.unregister(client)
        self.assertEqual(len(self.registry.clients), 0)

    def test_get_client(self):
        self.registry.flush()
        client = get_ws_client()
        self.registry.register(client)
        self.registry.register(client)
        _client = self.registry.get_client(client.address)
        self.assertEqual(client, _client)


class JSONRPCApiTestCase(unittest.TestCase):
    def setUp(self):
        self.client = get_ws_client()
        self.socket_registry = SocketRegistry()
        self.socket_registry.register(self.client)

    def test_subscribe(self):
        request = JSONRPC20Request(
            'subscribe',
            {'address': self.client.address, 'channel': 'chat'}
        )
        response = JSONRPCResponseManager.handle(request.json, dispatcher)
        self.assertEqual(response.data['result'], True)

        self.assertEqual(len(registry.channels), 1)
        self.assertEqual(len(registry.subscribers), 1)

    def test_unsubscribe(self):
        registry.flush_all()
        registry.subscribe('chat', self.client)

        subscribers = registry.get_channel_subscribers('chat')
        self.assertEqual(len(subscribers), 1)

        request = JSONRPC20Request(
            'unsubscribe',
            {'address': self.client.address, 'channel': 'chat'}
        )
        response = JSONRPCResponseManager.handle(request.json, dispatcher)
        self.assertEqual(response.data['result'], True)
        subscribers = registry.get_channel_subscribers('chat')
        self.assertEqual(len(subscribers), 0)

    def test_emit(self):
        registry.flush_all()
        client_1 = get_ws_client()
        client_2 = get_ws_client()
        client_3 = get_ws_client()

        registry.subscribe('chat', client_1, client_2, client_3)
        self.assertEqual(len(registry.channels), 1)
        self.assertEqual(len(registry.subscribers), 3)

        request = JSONRPC20Request(
            'emit',
            {'data': {'message': 'test'}, 'channel': 'chat'}
        )
        response = JSONRPCResponseManager.handle(request.json, dispatcher)
        self.assertEqual(response.data['result'], True)

        for client in client_1, client_2, client_3:
            # mock for send method is injected in get_ws_client
            client.ws.send.assert_called_once_with('{"message": "test"}')
