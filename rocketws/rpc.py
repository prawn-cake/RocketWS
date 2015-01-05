# -*- coding: utf-8 -*-
""" All json rpc methods is defined here.
There are two type of methods to dispatch:
    * ui_dispatch rpc methods are defined for WebSockets messages from UI
    * ms_dispatch rpc methods are defined for messages sources handlers
"""

import logbook
from jsonrpc import dispatcher as ui_dispatcher, Dispatcher
from rocketws.registry import ChannelRegistry, SocketRegistry

logger = logbook.Logger('jsonrpc')

registry = ChannelRegistry()
socket_registry = SocketRegistry()
ms_dispatcher = Dispatcher()  # messages_source dispatcher


@ui_dispatcher.add_method
def subscribe(channel, address):
    # TODO: add support of private channels which start with `_`,
    # `_my_private_channel` for example, pass some id and check that all
    # clients have the same id
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


@ms_dispatcher.add_method
def emit(channel, data):
    logger.info('invoke `emit` command, args: {}'.format((channel, data)))
    return registry.emit(channel, data)