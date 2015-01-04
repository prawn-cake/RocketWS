# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()

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

    def test_send_message(self):
        source = get_configured_messages_source(self.source_name)
        source.start()
        self.assertTrue(source.started)

        url = 'http://localhost:{}/'.format(source.server.server_port)
        response = requests.post(url, json=dict(a=1))
        self.assertEqual(response.status_code, 200, response.content)

        source.stop()
        self.assertFalse(source.started)


class RabbitMQMessagesSourceTestCase(unittest.TestCase):
    def setUp(self):
        self.source_name = 'rabbitmq'

    def test_configurator(self):
        source = get_configured_messages_source(self.source_name)
        self.assertIsInstance(source, RabbitMQMessagesSource)

    # @unittest.skip('source is not completely implemented')
    def test_start_stop(self):
        source = get_configured_messages_source(self.source_name)
        source.start()
        self.assertTrue(source.started)
        source.stop()
        self.assertFalse(source.started)