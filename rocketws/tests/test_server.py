# -*- coding: utf-8 -*-
import unittest

from rocketws.server import MainApplication, run_server
from mock import MagicMock, patch
from rocketws.registry import SocketRegistry
from rocketws.tests.test_base import get_ws_client


class MainApplicationTest(unittest.TestCase):
    def setUp(self):
        client = get_ws_client(port=1111)
        ws = MagicMock(handler=MagicMock(active_client=client))
        self.server = MainApplication(ws=ws)
        self.socket_registry = SocketRegistry()
        self.socket_registry.flush()

    def test_on_open_on_close(self):
        self.assertEqual(self.server.active_client.address[1], 1111)
        self.assertEqual(len(self.socket_registry.clients), 0)

        # Server must registers active client in socket registry after open
        # connection
        self.server.on_open()
        self.assertEqual(len(self.socket_registry.clients), 1)

        self.server.on_close()
        self.assertEqual(len(self.socket_registry.clients), 0)

    def test_on_message(self):
        # TODO: to implement
        pass

    @patch('rocketws.transport.http.HTTPTransport.start')
    @patch('gevent.pywsgi.WSGIServer.serve_forever')
    def test_run_server(self, mock_serve, mock_transport_start):
        run_server()
        self.assertTrue(mock_serve.called)
        self.assertTrue(mock_transport_start.called)