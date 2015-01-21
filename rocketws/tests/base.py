# -*- coding: utf-8 -*-
import unittest
from random import randint

from rocketws.exceptions import ImproperlyConfigured
from geventwebsocket.handler import Client
import mock
from rocketws.messages_sources.base import BaseMessagesSource


def get_ws_client(address='127.0.0.1', port=None):
    if port is None:
        port = randint(10000, 65535)
    client = Client(address=tuple([address, port]), ws=mock.MagicMock())
    client.ws.send = mock.MagicMock(return_value=True)
    return client


class ModelsTestCase(unittest.TestCase):
    def test_base_message_source(self):
        class ConcreteMessagesSource(BaseMessagesSource):
            pass

        # Can't instantiate abstract class with abstract methods start, stop
        self.assertRaises(TypeError, ConcreteMessagesSource)

        class ConcreteMessagesSource2(BaseMessagesSource):
            def start(self):
                pass

            def stop(self):
                pass

        # Can't instantiate MessagesSource with un-callable callback
        self.assertRaises(
            ValueError, ConcreteMessagesSource2, 'not a function')


class CommonMethodsTestCase(unittest.TestCase):
    def test_get_configured_messages_source(self):
        from rocketws.server import get_configured_messages_source

        http_source = get_configured_messages_source(name='http')
        self.assertIsInstance(http_source, BaseMessagesSource)

        self.assertRaises(
            ImproperlyConfigured,
            get_configured_messages_source,
            name='unknown'
        )