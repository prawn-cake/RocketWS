# -*- coding: utf-8 -*-
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from simplemodels.models import DictEmbeddedDocument
from simplemodels.fields import SimpleField


class Message(DictEmbeddedDocument):
    type = SimpleField()
    data = SimpleField()


class EchoApplication(WebSocketApplication):
    # NOTE: access to all clients self.ws.handler.server.clients.values()

    def on_open(self, *args, **kwargs):
        print('On open: {}'.format(self.clients))
        print(self.active_client)

    def on_close(self, *args, **kwargs):
        print('On close: {}'.format(self.clients))
        print(self.active_client)

    def on_message(self, message, *args, **kwargs):
        print('on message: {}, {}, {}'.format(message, args, kwargs))
        print(self.active_client.__dict__)

    @property
    def clients(self):
        return self.ws.handler.server.clients

    @property
    def active_client(self):
        """ Return active client

        :return: geventwebsocket.handler.Client
        """
        return self.ws.handler.active_client


resources = Resource({
    '/echo': EchoApplication
})

DEBUG = True
PORT = 8000
HOST = ''
server = WebSocketServer((HOST, PORT), resources, debug=DEBUG)
# For sending ws messages to

if __name__ == '__main__':
    server.serve_forever()