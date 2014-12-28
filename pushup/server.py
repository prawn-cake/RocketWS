# -*- coding: utf-8 -*-
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from pushup.registry import AliasRegistry
from simplemodels.models import DictEmbeddedDocument
from simplemodels.fields import SimpleField
import json
from jsonrpc import JSONRPCResponseManager, dispatcher


class Message(DictEmbeddedDocument):
    method = SimpleField()
    data = SimpleField()


class EchoApplication(WebSocketApplication):
    # NOTE: access to all clients self.ws.handler.server.clients.values()

    def on_open(self, *args, **kwargs):
        print('On open: {}'.format(self.clients))
        print(self.active_client)

    def on_close(self, *args, **kwargs):
        print('On close: {}'.format(self.clients))
        print(self.active_client)
        print(registry.sessions)
        # TODO: remove alias

    def on_message(self, message, *args, **kwargs):
        print('on message: {}, {}, {}'.format(message, args, kwargs))
        print(self.active_client)
        # TODO: add alias handler for current client
        if message is None:
            return None

        message = self._inject_active_client(message)
        response = JSONRPCResponseManager.handle(message, dispatcher)

        return response.data

    def _inject_active_client(self, message):
        """Inject active_client for jsonrpc handler

        :param message:
        :return:
        """
        try:
            json_data = json.loads(message)
        except ValueError:
            return message
        else:
            json_data['params']['active_client'] = self.active_client
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


# JSON-RPC methods

@dispatcher.add_method
def register_alias(alias, active_client):
    registry.add_alias(alias, active_client)


resources = Resource({
    '/echo': EchoApplication
})

DEBUG = True
PORT = 8000
HOST = ''
server = WebSocketServer((HOST, PORT), resources, debug=DEBUG)
registry = AliasRegistry()

if __name__ == '__main__':
    server.serve_forever()