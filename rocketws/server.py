# -*- coding: utf-8 -*-
import sys
import os.path as op

# PYTHON_PATH project visibility
sys.path.append(op.abspath(op.dirname(__file__)) + '/../')

from gevent import monkey
monkey.patch_all()

import json
import importlib

from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from rocketws.exceptions import ImproperlyConfigured
from jsonrpc import JSONRPCResponseManager
import settings
import logbook
from rocketws.rpc import (
    registry, socket_registry, ui_dispatcher, ms_dispatcher
)


logger = logbook.Logger('server')


class EchoApplication(WebSocketApplication):
    # NOTE: access to all clients self.ws.handler.server.clients.values()

    def on_open(self, *args, **kwargs):
        logger.debug('On open: {}'.format(self.clients))
        logger.debug('Active client: {}'.format(self.active_client))

        socket_registry.register(self.active_client)

    def on_close(self, *args, **kwargs):
        logger.debug('On close: {}'.format(self.clients))
        logger.debug('Active client: {}'.format(self.active_client))
        socket_registry.unregister(self.active_client)
        logger.debug('subscribers: {}'.format(registry.subscribers))

    def on_message(self, message, *args, **kwargs):
        logger.debug('on message: {}, {}, {}'.format(message, args, kwargs))
        if message is None:
            return None

        message = self._inject_client_address(message)
        response = JSONRPCResponseManager.handle(message, ui_dispatcher)
        logger.debug('subscribers: {}'.format(registry.subscribers))
        return response.data

    def _inject_client_address(self, message):
        """Inject active_client for jsonrpc handler

        :param message:
        :return:
        """
        try:
            json_data = json.loads(message)
        except ValueError:
            return message
        else:
            json_data['params']['address'] = self.active_client.address
        return json.dumps(json_data)

    @property
    def clients(self):
        return self.ws.handler.server.clients

    @property
    def active_client(self):
        """ Return active client

        :return: geventwebsocket.handler.Client
        """
        return self.ws.handler.active_client


# TODO: add implementation of multiple resources and auto-configuring it
# TODO: implement own registry and socket registry for each WebSocketsApplication
resources = Resource({
    '/echo': EchoApplication
})


def get_configured_messages_source(name=None):
    """Dynamic import for messages source

    :return: BaseMessagesSource implementation instance
    :raise ImproperlyConfigured:
    """
    pkg = importlib.import_module(
        'rocketws.messages_sources.{}'.format(
            name or settings.MESSAGES_SOURCE['ADAPTER']))
    try:
        source_cls = pkg.__dict__['source']
    except KeyError:
        raise ImproperlyConfigured(
            'Wrong MESSAGES_SOURCE adapter: {}'.format(
                settings.MESSAGES_SOURCE['ADAPTER']))

    def on_message_callback(raw_message):
        response = JSONRPCResponseManager.handle(raw_message, ms_dispatcher)
        return response.data

    source = source_cls(on_message_callback, **settings.MESSAGES_SOURCE)
    logger.debug('Configure messages source `{}`'.format(
        name or settings.MESSAGES_SOURCE['ADAPTER']))
    return source


# TODO: add daemonization (supervisor or gunicorn or as a linux daemon)
if __name__ == '__main__':
    logger.info('Starting all services')
    server = WebSocketServer(
        (settings.WEBSOCKETS['HOST'], settings.WEBSOCKETS['PORT']),
        resources,
        debug=settings.WEBSOCKETS['DEBUG']
    )
    server.environ['SERVER_SOFTWARE'] = ''
    messages_source = get_configured_messages_source()
    try:
        messages_source.start()
        logger.info('Starting WebSocketServer on: {}'.format(server.address))
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info('catch KeyboardInterrupt, stop all services')
        server.stop()
        messages_source.stop()
        socket_registry.flush()
        registry.flush_all()