# -*- coding: utf-8 -*-

from rocketws.exceptions import ImproperlyConfigured
from rocketws.transport.base import BaseTransport

try:
    import flask
except ImportError as err:
    raise ImproperlyConfigured('Error loading flask module: {}'.format(err))
else:
    from flask import request
import logging


logger = logging.getLogger('ms:http')


class HTTPTransport(BaseTransport):
    def __init__(self, on_message_callback, *args, **conn_params):
        super(HTTPTransport, self).__init__(on_message_callback, *args,
                                                 **conn_params)
        self.app = flask.Flask(self.__class__.__name__)

        def handle_view():
            logger.info(
                'invoke handle_view, request data: {}'.format(request.data))
            return str(on_message_callback(request.data))
            # return "Hello"

        handle_view.methods = ['POST']
        self.app.add_url_rule('/', view_func=handle_view)
        from gevent.pywsgi import WSGIServer

        self.server = WSGIServer(
            (conn_params.get('HOST', ''), conn_params.get('PORT', 8003)),
            application=self.app
        )

    def start(self):
        logger.debug(
            'Starting HTTP transport on: {}'.format(self.server.address))
        self.server.start()
        logger.debug('Done')

    def stop(self):
        logger.info('Stopping HTTP transport')
        self.server.stop()
        logger.debug('Done')

    @property
    def started(self):
        return self.server.started


source = HTTPTransport
__all__ = ['source']
