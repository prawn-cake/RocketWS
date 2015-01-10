# -*- coding: utf-8 -*-
""" All json rpc methods is defined here.
There are two type of methods to dispatch:
    * ui_dispatch rpc methods are defined for WebSockets messages from UI
    * ms_dispatch rpc methods are defined for messages sources handlers
"""

import logbook
from jsonrpc import dispatcher as ui_dispatcher, Dispatcher
from rocketws.exceptions import RPCMethodError
from rocketws.registry import ChannelRegistry, SocketRegistry

logger = logbook.Logger('jsonrpc:ui')

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
def send_data(channel, data, address):
    # TODO: rename the method
    logger.info('invoke `send_data` command, args: {}'.format(
        (channel, address)))
    client = socket_registry.get_client(address)
    if not registry.is_client_in_channel(client, channel):
        msg = 'Client `{}` is not a subscriber of the channel `{}`'.format(
            address, channel)
        logger.error('Error: {}; Data: {}'.format(msg, data))
        raise RPCMethodError(msg)

    # FIXME: think about whether we need to omit send message for sender or not
    # return registry.emit(channel, data, ignore_clients=(client.address, ))

    return registry.emit(channel, data)


# MessagesSources

logger_ms = logbook.Logger('jsonrpc:ms')


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
def notify_all(data):
    logger_ms.info('invoke `notify_all` command, args: {}'.format(data))
    return registry.notify_all(data)