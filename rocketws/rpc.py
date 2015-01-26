# -*- coding: utf-8 -*-
""" All json rpc methods is defined here.
There are two type of methods to dispatch:
    * ui_dispatch rpc methods are defined for WebSockets messages from UI
    * ms_dispatch rpc methods are defined for messages sources handlers
"""

import logging
from jsonrpc import dispatcher as ui_dispatcher, Dispatcher
from rocketws.exceptions import RPCMethodError
from rocketws.helpers import log_methods_time
from rocketws.registry import ChannelRegistry, SocketRegistry

logger = logging.getLogger('jsonrpc:ui')

registry = ChannelRegistry()
socket_registry = SocketRegistry()
ms_dispatcher = Dispatcher()  # messages_source dispatcher


@ui_dispatcher.add_method
def subscribe(channel, address):
    """Subscribe client to a channel

    :param channel: string name of channel
    NOTE: Private channels look the same as public but have super-secret names

    :param address: (ip, port) of client, this parameter is automatically
    injected by WS application
    :return:
    """
    logger.info('invoke `subscribe` command, args: {}'.format(
        (channel, address)))
    client = socket_registry.get_client(address)
    return registry.subscribe(channel, client)


@ui_dispatcher.add_method
def unsubscribe(channel, address):
    logger.info('invoke `unsubscribe` command, args: {}'.format(
        (channel, address)))
    client = socket_registry.get_client(address)
    return registry.unsubscribe(channel, client)


@ui_dispatcher.add_method
@log_methods_time(logger=logger)
def send_data(channel, data, address):
    """

    :param channel:
    :param data:
    :param address: is injected automatically
    :return: :raise RPCMethodError:
    """
    logger.info('invoke `send_data` command, args: {}'.format(
        (channel, address)))
    client = socket_registry.get_client(address)
    if not registry.is_client_in_channel(client, channel):
        msg = 'Client `{}` is not a subscriber of the channel `{}`'.format(
            address, channel)
        logger.error('Error: {}; Data: {}'.format(msg, data))
        raise RPCMethodError(msg)

    return registry.emit(channel, data, ignore_clients=(client.address, ))


@ui_dispatcher.add_method
def heartbeat(address):
    """UI heartbeat

    :return:
    """
    len_clients = len(socket_registry.clients)
    len_channels = len(registry.channels)
    logger_ms.info('heartbeat from `{}`:ok (clients={}; channels='
                   '{}))'.format(address, len_clients, len_channels))
    return {'heartbeat': 'ok'}


# MessagesSources

logger_ms = logging.getLogger('jsonrpc:ms')


@ms_dispatcher.add_method
def emit(channel, data):
    """RPC method for MessagesSources dispatcher (it means is used only by
    backend applications). Emit `data` for all subscribers in `channel`

    :param channel: string name
    :param data: dict-like data
    :return:
    """
    logger_ms.info('invoke `emit` command, args: {}'.format((channel, data)))
    return registry.emit(channel, data)


@ms_dispatcher.add_method
@log_methods_time(logger=logger)
def notify_all(data):
    logger_ms.info('invoke `notify_all` command, args: {}'.format(data))
    return registry.notify_all(data)


@ms_dispatcher.add_method
def total_subscribers(channel=None):
    logger_ms.info(
        'invoke `total_subscribers` command, args: {}'.format(channel))

    if channel is None:
        clients = registry.subscribers
    else:
        clients = registry.get_channel_subscribers(channel)
    return [c.address for c in clients]


@ms_dispatcher.add_method
def available_channels():
    logger_ms.info('invoke `available_channels` command')
    return registry.channels


@ms_dispatcher.add_method
def flush_dead_clients():
    logger_ms.info('invoke `flush_dead_clients` command')
    return registry.flush_dead_clients()


@ms_dispatcher.add_method
def heartbeat():
    """MessagesSource heartbeat

    :return:
    """
    logger_ms.info('heartbeat:ok')
    return {'heartbeat': 'ok'}