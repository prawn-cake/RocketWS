# -*- coding: utf-8 -*-
import unittest

from rocketws.server import get_configured_messages_source
from rocketws.messages_sources.http import HTTPMessagesSource
from rocketws.messages_sources.rabbitmq import RabbitMQMessagesSource
import requests


class HttpMessagesSourceTestCase(unittest.TestCase):
    def setUp(self):
        self.source_name = 'http'

    def test_configurator(self):
        source = get_configured_messages_source(self.source_name)
        self.assertIsInstance(source, HTTPMessagesSource)

    def test_start_stop(self):
        source = get_configured_messages_source(self.source_name)
        source.start()
        self.assertTrue(source.started)
        source.stop()
        self.assertFalse(source.started)

    def test_emit(self):
        source = get_configured_messages_source(self.source_name)
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


class RabbitMQMessagesSourceTestCase(unittest.TestCase):
    def setUp(self):
        self.source_name = 'rabbitmq'

    def test_configurator(self):
        source = get_configured_messages_source(self.source_name)
        self.assertIsInstance(source, RabbitMQMessagesSource)

    def test_start_stop(self):
        source = get_configured_messages_source(self.source_name)
        source.start()
        self.assertTrue(source.started)
        source.stop()
        self.assertFalse(source.started)