# -*- coding: utf-8 -*-
import unittest

from rocketws.server import MainApplication
from mock import MagicMock
from rocketws.tests import get_ws_client
from rocketws.registry import SocketRegistry


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