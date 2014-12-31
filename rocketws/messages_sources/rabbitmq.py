# -*- coding: utf-8 -*-
"""
Async rmq abstract manager
https://pika.readthedocs.org/en/latest/examples/asynchronous_consumer_example.html # noqa

NOTE: pika doesn't support python3
"""

try:
    import pika
except ImportError as err:
    raise ImproperlyConfigured('Error loading pika module: {}'.format(err))
else:
    from pika import PlainCredentials, ConnectionParameters, SelectConnection

import gevent
from rocketws.exceptions import ImproperlyConfigured
from rocketws.messages_sources.base import BaseMessagesSource
import logbook


pika.adapters.select_connection.SELECT_TYPE = 'epoll'
# pika_logger = get_logger(name='pika', log_level='INFO')

logger = logbook.Logger('ms:rabbitmq')


class RabbitMQMessagesSource(BaseMessagesSource):
    """RabbitMQ message source

    """

    def __init__(self, on_message_callback, **conn_params):
        super(RabbitMQMessagesSource, self).__init__(
            on_message_callback, **conn_params)

        self.listen_queue = conn_params['LISTEN_QUEUE']
        self.conn_params = ConnectionParameters(
            host=conn_params['HOST'],
            port=conn_params['PORT'],
            credentials=PlainCredentials(
                conn_params['USERNAME'], conn_params['PASSWORD']
            ),
            virtual_host=conn_params.get('VIRTUAL_HOST', '/'),
            channel_max=conn_params.get('CHANNEL_MAX', 100),
            socket_timeout=conn_params.get('SOCKET_TIMEOUT', 1),
            connection_attempts=conn_params.get('CONNECTION_ATTEMPTS', 10),
        )
        self._connection = None
        self._channel = None
        self.in_process = False
        self.message_ttl = conn_params.get('MESSAGE_TTL', 3600)
        self._consumer_tag = None
        self._closing = False

    def get_connection(self):
        return SelectConnection(
            self.conn_params,
            self._on_connection_open,
            stop_ioloop_on_close=False
        )

    def reconnect(self):
        """ Reconnect method. Useful for auto-reconnect functionality.
        """

        self._connection.ioloop.stop()
        if not self._closing:
            self._connection = self.get_connection()
            self._connection.ioloop.start()

    def open_channel(self):
        self._connection.channel(on_open_callback=self._on_channel_open)

    def _on_connection_open(self, conn):
        logger.info('RabbitMQ connection is opened')
        logger.info(self.conn_params)
        conn.add_on_close_callback(self._on_connection_closed)
        self.open_channel()

    def _on_channel_open(self, new_channel):
        self._channel = new_channel
        self.setup_queue(self._channel, self.listen_queue)

    def setup_queue(self, channel, queue_name):
        channel.queue_declare(
            queue=queue_name,
            durable=True,
            callback=self._on_queue_declared,
            arguments={'x-message-ttl': self.message_ttl}
        )

    def _on_queue_declared(self, frame):
        """
        Called when RabbitMQ has told us our Queue has been declared,
        frame is the response from RabbitMQ
        """
        self.start_consuming()

    def start_consuming(self):
        """
        Set consumer tag and start basic consume
        """
        self._consumer_tag = self._channel.basic_consume(
            self._handle, queue=self.listen_queue)

    def _handle(self, ch, method, properties, body):
        """
        Handle rmq message method
        :param ch: channel obj
        :param method:
        :param properties:
        :param body:
        """
        ch.basic_ack(method.delivery_tag)
        self.in_process = True
        # All parameters could be passed, but seems no need
        self.on_message_callback(body)
        self.in_process = False

    def _run(self):
        self._connection = self.get_connection()
        self._connection.ioloop.start()

    def stop_consuming(self):
        """Stop message consuming.
        Send cancel signal to RabbitMQ for correct interruption.

        """
        if self._channel:
            logger.info("Sending `Basic.Cancel` tag to RabbitMQ")

            cancel_fn = lambda unused_frame: self.close_channel \
                if self._channel else None
            self._channel.basic_cancel(cancel_fn, self._consumer_tag)

    def close_channel(self):
        self._channel.close()

    def _on_connection_closed(self, conn=None, reply_code=None,
                              reply_text=None):
        """ Set in open connection method
        """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            logger.warning(
                "Connection closed, reconnect in 5 seconds: ({}) {}".format(
                    reply_code, reply_text)
            )
            gevent.sleep(5)
            self.reconnect()
            # self._connection.add_timeout(5, self.reconnect)

    def stop(self):
        logger.info('Stopping')
        self._closing = True
        self.stop_consuming()
        if self._connection:
            self._connection.ioloop.stop()
        return super(RabbitMQMessagesSource, self).stop()


source = RabbitMQMessagesSource
__all__ = ['source']