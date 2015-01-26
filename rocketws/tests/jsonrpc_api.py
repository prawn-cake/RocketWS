# -*- coding: utf-8 -*-
import unittest

from jsonrpc import JSONRPCResponseManager
from jsonrpc.jsonrpc2 import JSONRPC20Request
from rocketws.registry import SocketRegistry
from rocketws.rpc import registry, ms_dispatcher, ui_dispatcher
from rocketws.tests import get_ws_client


class JSONRPCWebSocketsApiTestCase(unittest.TestCase):
    def setUp(self):
        self.client = get_ws_client()
        self.socket_registry = SocketRegistry()
        self.socket_registry.register(self.client)

    def test_subscribe(self):
        request = JSONRPC20Request(
            'subscribe',
            {'address': self.client.address, 'channel': 'chat'}
        )
        response = JSONRPCResponseManager.handle(request.json, ui_dispatcher)
        self.assertIn('subscribed', response.data['result'])

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
        response = JSONRPCResponseManager.handle(request.json, ui_dispatcher)
        self.assertIn('unsubscribed', response.data['result'])
        subscribers = registry.get_channel_subscribers('chat')
        self.assertEqual(len(subscribers), 0)

    def test_emit(self):
        """Test for backend emit command
        """
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
        response = JSONRPCResponseManager.handle(request.json, ms_dispatcher)
        self.assertIn('emitted', response.data['result'])

        for client in client_1, client_2, client_3:
            # mock for send method is injected in get_ws_client
            # message type will be added automatically
            self.assertEqual(client.ws.send.call_count, 1)
            str_call = str(client.ws.send.call_args_list[0])
            self.assertIn('"message": "test"', str_call)
            self.assertIn('"__type": "message"}', str_call)
            self.assertIn('"__ts":', str_call)

    def test_send_data(self):
        """Test ui send_data.

        """
        registry.flush_all()
        client_1 = get_ws_client()
        client_2 = get_ws_client()

        # Emulate WebSocketApplication server registration
        self.socket_registry.register(client_1, client_2)

        registry.subscribe('chat', client_1, client_2)

        # Assume that client1 send message to chat
        request = JSONRPC20Request(
            'send_data',
            {
                'data': {'message': 'test', 'type': 'my_type'},
                'channel': 'chat',
                'address': client_1.address
            }
        )
        response = JSONRPCResponseManager.handle(request.json, ui_dispatcher)
        self.assertIn('emitted', response.data['result'])

        # only client 2 receives a message
        for client in client_2, :
            # mock for send method is injected in get_ws_client
            self.assertEqual(client.ws.send.call_count, 1)
            str_call = str(client.ws.send.call_args_list[0])
            self.assertIn('"message": "test"', str_call)
            self.assertIn('"__type": "message"}', str_call)
            self.assertIn('"type": "my_type"', str_call)
            self.assertIn('"__ts":', str_call)

        # Not subscribed client3 send message to `chat`, expected an error
        client_3 = get_ws_client()

        # Emulate WebSocketApplication server registration
        self.socket_registry.register(client_3)

        request = JSONRPC20Request(
            'send_data',
            {
                'data': {'message': 'test'},
                'channel': 'chat',
                'address': client_3.address
            }
        )
        response = JSONRPCResponseManager.handle(request.json, ui_dispatcher)
        self.assertTrue(response.data['error'])
        self.assertIn(
            'is not a subscriber of the channel `chat`', str(response.json))
        self.assertFalse(client_3.ws.send.called)

    def test_heartbeat(self):
        registry.flush_all()
        client_1 = get_ws_client()

        # Emulate WebSocketApplication server registration
        self.socket_registry.register(client_1)

        request = JSONRPC20Request('heartbeat', {'address': client_1.address})
        response = JSONRPCResponseManager.handle(request.json, ui_dispatcher)
        self.assertEqual(response.data['result'], {'heartbeat': 'ok'})