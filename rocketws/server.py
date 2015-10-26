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
import rocketws.settings as settings

import logging
import logging.config
logging.config.dictConfig(settings.LOGGING)

from rocketws.rpc import (
    registry, socket_registry, ui_dispatcher, transport_dispatcher
)


logger = logging.getLogger('server')


class MainApplication(WebSocketApplication):
    # NOTE: access to all clients self.ws.handler.server.clients.values()

    def on_open(self, *args, **kwargs):
        logger.debug('On open connection for {}'.format(
            self.active_client.address))
        socket_registry.register(self.active_client)
        logger.debug('total sockets={}; total subscribers={}'.format(
            len(socket_registry.clients), len(registry.subscribers)))

    def on_close(self, *args, **kwargs):
        logger.debug('On close connection for {}'.format(
            self.active_client.address))
        socket_registry.unregister(self.active_client)
        logger.debug('total sockets={}; total subscribers={}'.format(
            len(socket_registry.clients), len(registry.subscribers)))

    def on_message(self, message, *args, **kwargs):
        logger.debug('on message: {}, {}, {}'.format(message, args, kwargs))
        if message is None:
            return None

        message = self._inject_client_address(message)
        response = JSONRPCResponseManager.handle(message, ui_dispatcher)

        # Send response to the client
        self.active_client.ws.send(response.json)

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


# TODO: think about implementation of multiple resources and auto-configuring
# it
# --> implement own registry and socket registry for each WebSocketsApplication

# TODO: implement so-called garbage collector for dead subscribers to remove
# null-references automatically

resources = Resource({
    settings.WEBSOCKETS['LOCATION']: MainApplication
})


def get_configured_transport(name=None, host=None, port=None):
    """Dynamic import for transport

    :return: BaseMessagesSource implementation instance
    :raise ImproperlyConfigured:
    """
    try:
        pkg = importlib.import_module(
            'rocketws.transport.{}'.format(
                name or settings.TRANSPORT['ADAPTER']))
    except ImportError as err:
        raise ImproperlyConfigured(err)

    try:
        source_cls = pkg.__dict__['source']
    except KeyError:
        raise ImproperlyConfigured(
            'Source is not found for adapter: {}'.format(
                settings.TRANSPORT['ADAPTER']))

    def on_message_callback(raw_message):
        response = JSONRPCResponseManager.handle(raw_message,
                                                 transport_dispatcher)
        return response.data

    if host:
        settings.TRANSPORT.update(HOST=host)
    if port:
        settings.TRANSPORT.update(PORT=port)

    source = source_cls(on_message_callback, **settings.TRANSPORT)
    logger.debug('Configure transport `{}`'.format(
        name or settings.TRANSPORT['ADAPTER']))
    return source


def run_server(ws_host=None, ws_port=None, transport_host=None,
               transport_port=None):
    """Application run method

    """
    logger.info('Starting all services')
    server = WebSocketServer(
        (ws_host or settings.WEBSOCKETS['HOST'],
         ws_port or settings.WEBSOCKETS['PORT']),
        resources,
        debug=settings.WEBSOCKETS['DEBUG']
    )
    server.environ['SERVER_SOFTWARE'] = ''
    messages_source = get_configured_transport(
        host=transport_host, port=transport_port)
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