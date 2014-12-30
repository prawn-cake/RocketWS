# -*- coding: utf-8 -*-
import json

from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from rocketws.registry import ChannelRegistry, SocketRegistry
from jsonrpc import JSONRPCResponseManager, dispatcher


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
            # FIXME: self.active_client is not JSON serializable
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

@dispatcher.add_method
def subscribe(channel, address):
    # TODO: add support of private channels which start with `_`,
    # `_my_private_channel` for example, pass some id and check that all
    # clients have the same id
    client = socket_registry.get_client(address)
    return registry.subscribe(channel, client)


@dispatcher.add_method
def unsubscribe(channel, address):
    client = socket_registry.get_client(address)
    return registry.unsubscribe(channel, client)


@dispatcher.add_method
def emit(channel, data):
    return registry.emit(channel, data)

resources = Resource({
    '/echo': EchoApplication
})

DEBUG = True
PORT = 8000
HOST = ''
server = WebSocketServer((HOST, PORT), resources, debug=DEBUG)
registry = ChannelRegistry()
socket_registry = SocketRegistry()

if __name__ == '__main__':
    # TODO: run with pywsgi server
    server.serve_forever()