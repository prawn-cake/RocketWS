# -*- coding: utf-8 -*-
from rocketws.exceptions import ImproperlyConfigured
from rocketws.messages_sources.base import BaseMessagesSource

try:
    import flask
except ImportError as err:
    raise ImproperlyConfigured('Error loading flask module: {}'.format(err))
else:
    from flask import request
import logbook


logger = logbook.Logger('ms:http')


class HTTPMessagesSource(BaseMessagesSource):
    def __init__(self, on_message_callback, *args, **conn_params):
        super(HTTPMessagesSource, self).__init__(
            on_message_callback, *args, **conn_params)

        self.app = flask.Flask(self.__class__.__name__)

        def index_view():
            logger.info('invoke index_view')
            on_message_callback(request.get_json(force=True))
            return {'a': 1}

        index_view.methods = ['POST']

        self.app.add_url_rule('/', view_func=index_view)

        from gevent.pywsgi import WSGIServer
        self.server = WSGIServer(
            (conn_params.get('HOST', ''), conn_params.get('PORT', 8003)),
            self.app
        )

    def _run(self, *args, **kwargs):
        logger.info('Starting server on {}'.format(self.server.address))
        self.server.start()

    def stop(self):
        logger.info('Stopping server')
        self.server.stop()
        return super(HTTPMessagesSource, self).stop()

    @property
    def started(self):
        return self.server.started


source = HTTPMessagesSource
__all__ = ['source']