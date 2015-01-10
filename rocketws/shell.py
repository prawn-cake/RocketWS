# -*- coding: utf-8 -*-
import sys
import os.path as op

# PYTHON_PATH project visibility
sys.path.append(op.abspath(op.dirname(__file__)) + '/../')

import cmd
import logbook
from rocketws import settings
import requests
import ujson as json


logger = logbook.Logger('registry')
CONNECT_URL = 'http://{HOST}:{PORT}/'.format(**settings.MESSAGES_SOURCE)


class RocketWSShell(cmd.Cmd):

    """RocketWS command line shell"""

    intro = "\nWelcome to RocketWS shell! Type `help` for help."
    prompt = '--> '

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.last_search_result = None

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

    def do_get_subscribers(self, line):
        """Get subscribers information

        """
        channel = get_input(
            'Enter a channel to get subscribers',
            default='all',
            validator=str
        )
        if channel == 'all':
            print(get_subscribers())
        else:
            print(get_subscribers(channel))

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


def emit_data(channel, data):
    logger.debug('emit_data for channel `{}`: {}'.format(channel, data))
    payload = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "emit",
        "params": {"channel": channel, "data": data}
    }
    try:
        response = requests.post(CONNECT_URL, json=payload)
    except requests.exceptions.ConnectionError as err:
        msg = 'Connection error to `{}`, ' \
              'check RocketWS is running'.format(CONNECT_URL)
        logger.error(err)
        print(msg)
    else:
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
    try:
        response = requests.post(CONNECT_URL, json=payload)
    except requests.exceptions.ConnectionError as err:
        msg = 'Connection error to `{}`, ' \
              'check RocketWS is running'.format(CONNECT_URL)
        logger.error(err)
        print(msg)
    else:
        logger.info('notify_all:ok {}'.format(response.status_code))
        return response.content


def get_subscribers(channel=None):
    logger.debug('get_subscribers for channel `{}`'.format(channel))
    payload = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "get_subscribers",
        "params": {"channel": channel}
    }
    try:
        response = requests.post(CONNECT_URL, json=payload)
    except requests.exceptions.ConnectionError as err:
        msg = 'Connection error to `{}`, ' \
              'check RocketWS is running'.format(CONNECT_URL)
        logger.error(err)
        print(msg)
    else:
        logger.info('get_subscribers:ok {}'.format(response.status_code))
        return response.content


if __name__ == '__main__':
    RocketWSShell().cmdloop()