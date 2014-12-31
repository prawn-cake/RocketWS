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
            on_message_callback(request.get_json(force=True))
            return True

        index_view.methods = ['POST']

        self.app.add_url_rule('/', index_view)

        from gevent.pywsgi import WSGIServer
        self.server = WSGIServer(
            (conn_params.get('HOST', ''), conn_params.get('PORT', 8003)),
            self.app
        )

    def _run(self):
        self.server.start()

    def stop(self):
        logger.info('Stopping')
        self.server.stop()
        return super(HTTPMessagesSource, self).stop()


source = HTTPMessagesSource
__all__ = ['source']