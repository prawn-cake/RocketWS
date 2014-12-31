# -*- coding: utf-8 -*-
import json

from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from rocketws.exceptions import ImproperlyConfigured
from rocketws.registry import ChannelRegistry, SocketRegistry
from jsonrpc import JSONRPCResponseManager, dispatcher
import settings
import logbook
import importlib


logger = logbook.Logger('server')


class EchoApplication(WebSocketApplication):
    # NOTE: access to all clients self.ws.handler.server.clients.values()

    def on_open(self, *args, **kwargs):
        print('On open: {}'.format(self.clients))
        print(self.active_client)
        socket_registry.register(self.active_client)

    def on_close(self, *args, **kwargs):
        print('On close: {}'.format(self.clients))
        print(self.active_client)
        print(registry.subscribers)
        socket_registry.unregister(self.active_client)

    def on_message(self, message, *args, **kwargs):
        print('on message: {}, {}, {}'.format(message, args, kwargs))
        print(self.active_client)
        if message is None:
            return None

        message = self._inject_client_address(message)
        response = JSONRPCResponseManager.handle(message, dispatcher)

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
        print('call clients: {}'.format(self.ws.handler.server.clients))
        return self.ws.handler.server.clients

    @property
    def active_client(self):
        """ Return active client

        :return: geventwebsocket.handler.Client
        """
        return self.ws.handler.active_client


# JSON-RPC methods

jsonrpc_log = logbook.Logger('jsonrpc')


@dispatcher.add_method
def subscribe(channel, address):
    # TODO: add support of private channels which start with `_`,
    # `_my_private_channel` for example, pass some id and check that all
    # clients have the same id
    jsonrpc_log.info('invoke `subscribe` command, args: {}'.format(
        (channel, address)))
    client = socket_registry.get_client(address)
    return registry.subscribe(channel, client)


@dispatcher.add_method
def unsubscribe(channel, address):
    jsonrpc_log.info('invoke `unsubscribe` command, args: {}'.format(
        (channel, address)))
    client = socket_registry.get_client(address)
    return registry.unsubscribe(channel, client)


@dispatcher.add_method
def emit(channel, data):
    jsonrpc_log.info('invoke `emit` command, args: {}'.format((channel, data)))
    return registry.emit(channel, data)


# TODO: add implementation of multiple resources and auto-configuring it
# TODO: implement own registry and socket registry for each WebSocketsApplication
resources = Resource({
    '/echo': EchoApplication
})


def get_configured_messages_source():
    """Dynamic import for messages source

    :return: BaseMessagesSource implementation instance
    :raise ImproperlyConfigured:
    """
    pkg = importlib.import_module(
        'rocketws.messages_sources.{}'.format(
            settings.MESSAGES_SOURCE['ADAPTER']))
    try:
        source_cls = pkg.__dict__['source']
    except KeyError:
        raise ImproperlyConfigured(
            'Wrong MESSAGES_SOURCE adapter: {}'.format(
                settings.MESSAGES_SOURCE['ADAPTER']))

    def on_message_callback(raw_message):
        response = JSONRPCResponseManager.handle(raw_message, dispatcher)
        return response.data

    source = source_cls(on_message_callback, **settings.MESSAGES_SOURCE)
    return source


server = WebSocketServer(
    (settings.WEBSOCKETS['HOST'], settings.WEBSOCKETS['PORT']),
    resources,
    debug=settings.WEBSOCKETS['DEBUG']
)

registry = ChannelRegistry()
socket_registry = SocketRegistry()
messages_source = get_configured_messages_source()


if __name__ == '__main__':
    try:
        logger.info('Starting all services')
        messages_source.start()
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info('catch KeyboardInterrupt, stop all services')
        server.stop()
        messages_source.stop()
        socket_registry.flush()
        registry.flush_all()
