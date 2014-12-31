# -*- coding: utf-8 -*-
import unittest

from rocketws.server import get_configured_messages_source
from rocketws.messages_sources.http import HTTPMessagesSource
from rocketws.messages_sources.rabbitmq import RabbitMQMessagesSource


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

    # def test_send_message(self):
    #     source = get_configured_messages_source(self.source_name)
    #     source.start()
    #     self.assertTrue(source.started)

        # TODO: send http post message here


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