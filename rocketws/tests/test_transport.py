# -*- coding: utf-8 -*-
import unittest

from rocketws.server import get_configured_transport
from rocketws.transport.http import HTTPTransport
import requests


class HttpTransportTestCase(unittest.TestCase):
    def setUp(self):
        self.transport = 'http'

    def test_configurator(self):
        source = get_configured_transport(self.transport)
        self.assertIsInstance(source, HTTPTransport)

    def test_start_stop(self):
        source = get_configured_transport(self.transport)
        source.start()
        self.assertTrue(source.started)
        source.stop()
        self.assertFalse(source.started)

    def test_emit(self):
        source = get_configured_transport(self.transport)
        source.start()
        self.assertTrue(source.started)

        payload = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "emit",
            "params": {"channel": "chat", "data": {"message": "hello world"}}
        }

        url = 'http://localhost:{}/'.format(source.server.server_port)
        response = requests.post(url, json=payload)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIn('emitted', response.content)

        source.stop()
        self.assertFalse(source.started)

    def test_ping(self):
        source = get_configured_transport(self.transport)
        source.start()
        self.assertTrue(source.started)

        payload = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "ping"
        }

        url = 'http://localhost:{}/'.format(source.server.server_port)
        response = requests.post(url, json=payload)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIn("{'ping': 'ok'}", response.content)

        source.stop()
        self.assertFalse(source.started)
