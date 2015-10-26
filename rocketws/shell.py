# -*- coding: utf-8 -*-
import sys
import os.path as op


# PYTHON_PATH project visibility
from rocketws.exceptions import HeartbeatError

sys.path.append(op.abspath(op.dirname(__file__)) + '/../')

import cmd
import logging
import rocketws.settings as settings

import requests
import ujson as json
import re


URL_RE = re.compile(
    r'^(?:http|ftp|ws)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|'
    r'[A-Z0-9-]{2,}\.?)|'  # domain...

    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE
)
logger = logging.getLogger('shell')
CONNECT_URL = 'http://{HOST}:{PORT}/'.format(**settings.TRANSPORT)


class RocketWSShell(cmd.Cmd):

    """RocketWS command line shell"""

    intro = "\nWelcome to RocketWS shell! Type `help` for help."
    prompt = '--> '

    def __init__(self, conn_url=None):
        cmd.Cmd.__init__(self)
        self.last_search_result = None
        self.do_connect(conn_url or CONNECT_URL)

    def do_emit(self, line):
        """Emit data to channel"""

        channel = get_input(
            'Enter a channel, for example `chat`', validator=str)
        data = get_input(
            'Enter json data',
            default='{"message": "test"}',
            validator=json.loads
        )
        print(emit_data(channel, data))

    def do_notify_all(self, line):
        """Notify all subscribers. Broadcast method."""

        data = get_input(
            'Enter json data, to notify all subscribers',
            default='{"message": "test"}',
            validator=json.loads
        )
        print(notify_all(data))

    def do_total_subscribers(self, line):
        """Get subscribers information

        """
        channel = get_input(
            'Enter a channel to get subscribers',
            default='all',
            validator=str
        )
        if channel == 'all':
            print(total_subscribers())
        else:
            print(total_subscribers(channel))

    def do_available_channels(self, line):
        """Get available channels
        """
        print(get_available_channels())

    def do_connect(self, line):
        """Change connect url.
        Examples:
            http://example.com
            ws://example.com:80/
            wss://example.com:443/

        """
        global CONNECT_URL
        if re.match(URL_RE, line):
            CONNECT_URL = line
            do_heartbeat()
        else:
            print('Wrong url: {}. Correct example: '
                  'http://domain.com'.format(line))

    def do_exit(self, line):
        print('Bye!')
        return True

    def do_EOF(self, line):
        print('Bye!')
        return True


def get_input(input_str, default=None, validator=None):
    """Helper for user input

    :param input_str:
    :param default:
    :param validator: built-in or custom function with one argument
    :return: validated value

    Usage:
        price = get_input('500.00', default=100, validator=float)
    """

    value = None
    text = "{} [default: {}]: ".format(input_str, default)
    if default is None:
        text = "{}: ".format(input_str)

    while value is None:
        value = raw_input(text) or default
        if validator:
            try:
                value = validator(value)
            except ValueError:
                print('Invalid value: {}'.format(value))
                value = None

    return value


def do_request(json_payload):
    """Request helper

    :param json_payload:
    :return: :raise requests.exceptions.ConnectionError:
    """
    try:
        response = requests.post(CONNECT_URL, json=json_payload)
    except requests.exceptions.ConnectionError as err:
        msg = 'Connection error to `{}`, ' \
              'check that RocketWS is started'.format(CONNECT_URL)
        logger.error(err)
        raise requests.exceptions.ConnectionError(msg)
    return response


def emit_data(channel, data):
    logger.debug('emit_data for channel `{}`: {}'.format(channel, data))
    payload = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "emit",
        "params": {"channel": channel, "data": data}
    }
    response = do_request(payload)
    logger.info('emit_data:ok {}'.format(response.status_code))
    return response.content


def notify_all(data):
    logger.debug('notify_all data: {}'.format(data))
    payload = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "notify_all",
        "params": {"data": data}
    }
    response = do_request(payload)
    logger.info('notify_all:ok {}'.format(response.status_code))
    return response.content


def total_subscribers(channel=None):
    logger.debug(
        'getting total_subscribers for a channel `{}`'.format(channel))
    payload = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "total_subscribers",
        "params": {"channel": channel}
    }
    response = do_request(payload)
    logger.info('total_subscribers:ok: {}'.format(response.status_code))
    return response.content


def get_available_channels():
    payload = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "available_channels",
        "params": {}
    }
    response = do_request(payload)
    logger.info('available_channels:ok: {}'.format(response.status_code))
    return response.content


def do_heartbeat():
    payload = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "heartbeat"
    }
    response = do_request(payload)
    logger.info('heartbeat:ok: {}'.format(response.status_code))
    if response.status_code != 200:
        raise HeartbeatError(
            'Heartbeat is not succeed: {}'.format(response.content))
    return response.content